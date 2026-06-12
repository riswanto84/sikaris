from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from core.access import is_biro_umum_user, get_user_unit_kerja, require_user_unit_or_all
from core.listing import SearchListMixin
from .forms import PermohonanPenghapusanBMNForm
from .models import PermohonanPenghapusanBMN


class PermohonanPenghapusanAccessMixin(LoginRequiredMixin):
    scope_type = 'penghapusan_bmn'

    def get_scoped_queryset(self):
        qs = PermohonanPenghapusanBMN.objects.select_related(
            'unit_kerja', 'pemohon', 'kendaraan', 'rumah_negara', 'tanah_negara',
            'dibuat_oleh', 'diverifikasi_oleh'
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


class PermohonanPenghapusanListView(PermohonanPenghapusanAccessMixin, SearchListMixin):
    model = PermohonanPenghapusanBMN
    template_name = 'penghapusan/list.html'
    select_related = ['unit_kerja', 'pemohon', 'kendaraan', 'rumah_negara', 'tanah_negara']
    search_fields = [
        ('nomor_permohonan', 'Nomor Permohonan'),
        ('unit_kerja__nama_unit', 'Unit Kerja'),
        ('pemohon__nama', 'Nama Pemohon'),
        ('pemohon__nip', 'NIP Pemohon'),
        ('jenis_aset', 'Jenis Aset'),
        ('kode_barang', 'Kode Barang'),
        ('nup', 'NUP'),
        ('nama_barang', 'Nama Barang'),
        ('alasan_penghapusan', 'Alasan Penghapusan'),
        ('status', 'Status'),
        ('nomor_persetujuan', 'Nomor Persetujuan'),
        ('nomor_sk_penghapusan', 'Nomor SK Penghapusan'),
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


class PermohonanPenghapusanCreateView(PermohonanPenghapusanAccessMixin, CreateView):
    model = PermohonanPenghapusanBMN
    form_class = PermohonanPenghapusanBMNForm
    template_name = 'penghapusan/form.html'
    success_url = reverse_lazy('penghapusan:list')

    def form_valid(self, form):
        user = self.request.user
        if not is_biro_umum_user(user):
            unit = get_user_unit_kerja(user)
            if not unit:
                raise PermissionDenied('User belum memiliki Unit Kerja/Satker.')
            form.instance.unit_kerja = unit
            form.instance.status = 'DIAJUKAN'
        else:
            if not form.instance.status:
                form.instance.status = 'DIAJUKAN'

        form.instance.dibuat_oleh = user
        form.instance.diperbarui_oleh = user
        self._fill_asset_snapshot(form.instance)
        messages.success(self.request, 'Permohonan penghapusan BMN berhasil diajukan.')
        return super().form_valid(form)

    def _fill_asset_snapshot(self, obj):
        if obj.jenis_aset == 'KENDARAAN' and obj.kendaraan:
            k = obj.kendaraan
            obj.kode_barang = obj.kode_barang or k.kode_barang
            obj.nup = obj.nup or k.nup
            obj.nama_barang = obj.nama_barang or f'{k.nomor_polisi} - {k.merek} {k.tipe or ""}'.strip()
            obj.nilai_perolehan = obj.nilai_perolehan or k.nilai_perolehan
            obj.kondisi_barang = obj.kondisi_barang or k.get_kondisi_display()
            obj.lokasi_barang = obj.lokasi_barang or str(k.unit_kerja or '')
        elif obj.jenis_aset == 'RUMAH_NEGARA' and obj.rumah_negara:
            r = obj.rumah_negara
            obj.kode_barang = obj.kode_barang or r.kode_barang
            obj.nup = obj.nup or r.nup
            obj.nama_barang = obj.nama_barang or f'{r.kode_rumah} - {r.nama_rumah}'
            obj.nilai_perolehan = obj.nilai_perolehan or r.nilai_perolehan
            obj.kondisi_barang = obj.kondisi_barang or r.get_kondisi_display()
            obj.lokasi_barang = obj.lokasi_barang or r.alamat
        elif obj.jenis_aset == 'TANAH_NEGARA' and obj.tanah_negara:
            t = obj.tanah_negara
            obj.kode_barang = obj.kode_barang or t.kode_barang
            obj.nup = obj.nup or t.nup
            obj.nama_barang = obj.nama_barang or f'{t.kode_tanah} - {t.nama_tanah}'
            obj.nilai_perolehan = obj.nilai_perolehan or t.nilai_perolehan
            obj.kondisi_barang = obj.kondisi_barang or t.get_status_tanah_display()
            obj.lokasi_barang = obj.lokasi_barang or t.alamat


class PermohonanPenghapusanUpdateView(PermohonanPenghapusanAccessMixin, UpdateView):
    model = PermohonanPenghapusanBMN
    form_class = PermohonanPenghapusanBMNForm
    template_name = 'penghapusan/form.html'
    success_url = reverse_lazy('penghapusan:list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not is_biro_umum_user(request.user) and self.object.status not in ['DRAFT', 'DIAJUKAN', 'PERLU_PERBAIKAN']:
            raise PermissionDenied('Usulan yang sudah diproses Biro Umum tidak dapat diedit oleh unit kerja.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        form.instance.diperbarui_oleh = user
        if is_biro_umum_user(user):
            if form.instance.status in ['DIVERIFIKASI_BIRO', 'DISETUJUI', 'DITOLAK', 'PROSES_PENGHAPUSAN', 'SELESAI'] and not form.instance.tanggal_verifikasi:
                form.instance.tanggal_verifikasi = timezone.now().date()
                form.instance.diverifikasi_oleh = user
        else:
            form.instance.status = 'DIAJUKAN'
        messages.success(self.request, 'Permohonan penghapusan BMN berhasil diperbarui.')
        return super().form_valid(form)


class PermohonanPenghapusanDetailView(PermohonanPenghapusanAccessMixin, DetailView):
    model = PermohonanPenghapusanBMN
    template_name = 'penghapusan/detail.html'


class PermohonanPenghapusanDeleteView(PermohonanPenghapusanAccessMixin, SafeDeleteMixin, DeleteView):
    model = PermohonanPenghapusanBMN
    success_url = reverse_lazy('penghapusan:list')
    success_message = 'Permohonan penghapusan BMN berhasil dihapus.'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not is_biro_umum_user(request.user) and self.object.status not in ['DRAFT', 'DIAJUKAN', 'PERLU_PERBAIKAN']:
            raise PermissionDenied('Usulan yang sudah diproses Biro Umum tidak dapat dihapus oleh unit kerja.')
        return super().dispatch(request, *args, **kwargs)
