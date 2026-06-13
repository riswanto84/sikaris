from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from core.access import get_user_unit_kerja, is_biro_umum_user, require_user_unit_or_all
from core.listing import SearchListMixin
from .forms import PermohonanPSPBMNForm
from .models import PermohonanPSPBMN, FotoBarangPSP


class PermohonanPSPAccessMixin(LoginRequiredMixin):
    def get_scoped_queryset(self):
        qs = PermohonanPSPBMN.objects.select_related(
            'unit_kerja', 'pemohon', 'dibuat_oleh', 'diverifikasi_oleh'
        )
        if is_biro_umum_user(self.request.user):
            return qs
        unit_id = require_user_unit_or_all(self.request.user)
        return qs.filter(unit_kerja_id=unit_id)

    def get_queryset(self):
        return self.get_scoped_queryset()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SafeDeleteMixin:
    template_name = 'includes/confirm_delete.html'
    success_message = 'Data berhasil dihapus.'
    protected_message = 'Data tidak dapat dihapus karena masih digunakan oleh data lain.'

    def form_valid(self, form):
        try:
            messages.success(self.request, self.success_message)
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return redirect(self.get_success_url())


class PermohonanPSPListView(PermohonanPSPAccessMixin, SearchListMixin):
    model = PermohonanPSPBMN
    template_name = 'psp/list.html'
    select_related = ['unit_kerja', 'pemohon']
    search_fields = [
        ('nomor_permohonan', 'Nomor Permohonan'),
        ('unit_kerja__nama_unit', 'Unit Kerja'),
        ('pemohon__nama', 'Nama Pemohon'),
        ('pemohon__nip', 'NIP Pemohon'),
        ('jenis_barang', 'Jenis Barang'),
        ('status', 'Status'),
        ('nomor_sk_psp', 'Nomor SK PSP'),
    ]

    def get_queryset(self):
        qs = self.get_scoped_queryset()
        if self.select_related:
            qs = qs.select_related(*self.select_related)
        q = (self.request.GET.get('q') or '').strip()
        selected_field = (self.request.GET.get('search_field') or 'ALL').strip()
        if q and self.search_fields:
            available_fields = [field for field, _label in self.search_fields]
            fields_to_search = available_fields if selected_field == 'ALL' or selected_field not in available_fields else [selected_field]
            query = Q()
            for field in fields_to_search:
                query |= Q(**{f'{field}__icontains': q})
            qs = qs.filter(query)
        return qs



def _save_foto_barang_files(request, permohonan):
    for foto in request.FILES.getlist('foto_barang_files'):
        FotoBarangPSP.objects.create(
            permohonan=permohonan,
            foto=foto,
            diupload_oleh=request.user if request.user.is_authenticated else None,
        )

class PermohonanPSPCreateView(PermohonanPSPAccessMixin, CreateView):
    model = PermohonanPSPBMN
    form_class = PermohonanPSPBMNForm
    template_name = 'psp/form.html'
    success_url = reverse_lazy('psp:list')

    def form_valid(self, form):
        user = self.request.user
        if not is_biro_umum_user(user):
            unit = get_user_unit_kerja(user)
            if not unit:
                raise PermissionDenied('User belum memiliki Unit Kerja/Satker.')
            form.instance.unit_kerja = unit
            form.instance.status = 'DIAJUKAN'
        elif not form.instance.status:
            form.instance.status = 'DIAJUKAN'
        form.instance.dibuat_oleh = user
        form.instance.diperbarui_oleh = user
        form.instance.nama_barang = form.instance.nama_barang or form.instance.get_jenis_barang_display()
        response = super().form_valid(form)
        _save_foto_barang_files(self.request, self.object)
        messages.success(self.request, 'Permohonan PSP BMN berhasil diajukan.')
        return response

    def _fill_asset_snapshot(self, obj):
        if obj.jenis_barang == 'KENDARAAN' and obj.kendaraan:
            k = obj.kendaraan
            obj.kode_barang = obj.kode_barang or k.kode_barang
            obj.nup = obj.nup or k.nup
            obj.nama_barang = obj.nama_barang or f'{k.nomor_polisi} - {k.merek} {k.tipe or ""}'.strip()
            obj.nilai_psp = obj.nilai_psp or k.nilai_perolehan
            obj.kondisi_barang = obj.kondisi_barang or k.get_kondisi_display()
            obj.lokasi_barang = obj.lokasi_barang or str(k.unit_kerja or '')
        elif obj.jenis_barang == 'RUMAH_NEGARA' and obj.rumah_negara:
            r = obj.rumah_negara
            obj.kode_barang = obj.kode_barang or r.kode_barang
            obj.nup = obj.nup or r.nup
            obj.nama_barang = obj.nama_barang or f'{r.kode_rumah} - {r.nama_rumah}'
            obj.nilai_psp = obj.nilai_psp or r.nilai_perolehan
            obj.kondisi_barang = obj.kondisi_barang or r.get_kondisi_display()
            obj.lokasi_barang = obj.lokasi_barang or r.alamat
        elif obj.jenis_barang == 'TANAH_NEGARA' and obj.tanah_negara:
            t = obj.tanah_negara
            obj.kode_barang = obj.kode_barang or t.kode_barang
            obj.nup = obj.nup or t.nup
            obj.nama_barang = obj.nama_barang or f'{t.kode_tanah} - {t.nama_tanah}'
            obj.nilai_psp = obj.nilai_psp or t.nilai_perolehan
            obj.kondisi_barang = obj.kondisi_barang or (t.kondisi or t.status_tanah)
            obj.lokasi_barang = obj.lokasi_barang or t.alamat


class PermohonanPSPUpdateView(PermohonanPSPAccessMixin, UpdateView):
    model = PermohonanPSPBMN
    form_class = PermohonanPSPBMNForm
    template_name = 'psp/form.html'
    success_url = reverse_lazy('psp:list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not is_biro_umum_user(request.user) and self.object.status not in ['DRAFT', 'DIAJUKAN', 'PERLU_PERBAIKAN']:
            raise PermissionDenied('Usulan PSP yang sudah diproses Biro Umum tidak dapat diedit oleh unit kerja.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        form.instance.diperbarui_oleh = user
        if is_biro_umum_user(user):
            if form.instance.status in ['DIVERIFIKASI_BIRO', 'DISETUJUI', 'PROSES_PSP', 'DITOLAK', 'SELESAI'] and not form.instance.tanggal_verifikasi:
                form.instance.tanggal_verifikasi = timezone.now().date()
                form.instance.diverifikasi_oleh = user
        else:
            form.instance.status = 'DIAJUKAN'
        response = super().form_valid(form)
        _save_foto_barang_files(self.request, self.object)
        messages.success(self.request, 'Permohonan PSP BMN berhasil diperbarui.')
        return response


class PermohonanPSPDetailView(PermohonanPSPAccessMixin, DetailView):
    model = PermohonanPSPBMN
    template_name = 'psp/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['foto_barang_list'] = self.object.foto_barang_list.all()
        return ctx


class PermohonanPSPDeleteView(PermohonanPSPAccessMixin, SafeDeleteMixin, DeleteView):
    model = PermohonanPSPBMN
    success_url = reverse_lazy('psp:list')
    success_message = 'Permohonan PSP BMN berhasil dihapus.'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not is_biro_umum_user(request.user) and self.object.status not in ['DRAFT', 'DIAJUKAN', 'PERLU_PERBAIKAN']:
            raise PermissionDenied('Usulan PSP yang sudah diproses Biro Umum tidak dapat dihapus oleh unit kerja.')
        return super().dispatch(request, *args, **kwargs)
