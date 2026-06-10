from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from core.roles import BMNRequiredMixin, VehicleViewRequiredMixin, can_manage_master
from .models import (
    UnitKerja,
    Pegawai,
    Kendaraan,
    RumahDinas,
    FotoKendaraan,
    FotoRumahDinas,
)
from .forms import UnitKerjaForm, PegawaiForm, KendaraanForm, RumahDinasForm


class SearchListMixin(LoginRequiredMixin, ListView):
    paginate_by = 15
    search_fields = []

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')

        if q and self.search_fields:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': q})
            qs = qs.filter(query)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class UnitKerjaListView(BMNRequiredMixin, SearchListMixin):
    model = UnitKerja
    template_name = 'master/unitkerja_list.html'
    search_fields = ['nama_unit', 'keterangan']


class UnitKerjaCreateView(BMNRequiredMixin, CreateView):
    model = UnitKerja
    form_class = UnitKerjaForm
    template_name = 'master/form.html'
    success_url = reverse_lazy('master:unitkerja_list')


class UnitKerjaUpdateView(BMNRequiredMixin, UpdateView):
    model = UnitKerja
    form_class = UnitKerjaForm
    template_name = 'master/form.html'
    success_url = reverse_lazy('master:unitkerja_list')


class PegawaiListView(BMNRequiredMixin, SearchListMixin):
    model = Pegawai
    template_name = 'master/pegawai_list.html'
    search_fields = ['nip', 'nama', 'jabatan', 'unit_kerja__nama_unit']


class PegawaiCreateView(BMNRequiredMixin, CreateView):
    model = Pegawai
    form_class = PegawaiForm
    template_name = 'master/pegawai_form.html'
    success_url = reverse_lazy('master:pegawai_list')


class PegawaiUpdateView(BMNRequiredMixin, UpdateView):
    model = Pegawai
    form_class = PegawaiForm
    template_name = 'master/pegawai_form.html'
    success_url = reverse_lazy('master:pegawai_list')


@login_required
@require_POST
def pegawai_foto_delete(request, pk):
    if not can_manage_master(request.user):
        messages.error(request, 'Anda tidak memiliki hak akses untuk menghapus foto pegawai.')
        return redirect('dashboard')

    pegawai = get_object_or_404(Pegawai, pk=pk)

    if pegawai.foto:
        pegawai.foto.delete(save=False)
        pegawai.foto = None
        pegawai.save(update_fields=['foto', 'updated_at'])
        messages.success(request, 'Foto pegawai berhasil dihapus.')
    else:
        messages.info(request, 'Pegawai ini belum memiliki foto.')

    return redirect('master:pegawai_update', pk=pegawai.pk)


class KendaraanListView(VehicleViewRequiredMixin, SearchListMixin):
    model = Kendaraan
    template_name = 'master/kendaraan_list.html'
    search_fields = ['nomor_polisi', 'merek', 'tipe', 'unit_kerja__nama_unit']


class KendaraanPhotoMixin:
    template_name = 'master/kendaraan_form.html'
    success_url = reverse_lazy('master:kendaraan_list')

    def save_uploaded_photos(self, kendaraan):
        for foto in self.request.FILES.getlist('foto_kendaraan'):
            FotoKendaraan.objects.create(
                kendaraan=kendaraan,
                foto=foto,
                diupload_oleh=self.request.user if self.request.user.is_authenticated else None
            )

    def form_valid(self, form):
        response = super().form_valid(form)
        self.save_uploaded_photos(self.object)
        messages.success(self.request, 'Data kendaraan berhasil disimpan.')
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if getattr(self, 'object', None):
            ctx['foto_kendaraan_list'] = self.object.galeri_foto.all()
        else:
            ctx['foto_kendaraan_list'] = []

        return ctx


class KendaraanCreateView(BMNRequiredMixin, KendaraanPhotoMixin, CreateView):
    model = Kendaraan
    form_class = KendaraanForm


class KendaraanUpdateView(BMNRequiredMixin, KendaraanPhotoMixin, UpdateView):
    model = Kendaraan
    form_class = KendaraanForm


@login_required
@require_POST
def kendaraan_foto_delete(request, pk):
    if not can_manage_master(request.user):
        messages.error(request, 'Anda tidak memiliki hak akses untuk menghapus foto kendaraan.')
        return redirect('dashboard')

    foto = get_object_or_404(FotoKendaraan, pk=pk)
    kendaraan_id = foto.kendaraan_id
    foto.foto.delete(save=False)
    foto.delete()

    messages.success(request, 'Foto kendaraan berhasil dihapus.')
    return redirect('master:kendaraan_update', pk=kendaraan_id)


class RumahDinasListView(BMNRequiredMixin, SearchListMixin):
    model = RumahDinas
    template_name = 'master/rumah_list.html'
    search_fields = ['kode_rumah', 'nama_rumah', 'alamat']


class RumahDinasPhotoMixin:
    template_name = 'master/rumah_form.html'
    success_url = reverse_lazy('master:rumah_list')

    def save_uploaded_photos(self, rumah_dinas):
        for foto in self.request.FILES.getlist('foto_rumah_dinas'):
            FotoRumahDinas.objects.create(
                rumah_dinas=rumah_dinas,
                foto=foto,
                diupload_oleh=self.request.user if self.request.user.is_authenticated else None
            )

    def form_valid(self, form):
        response = super().form_valid(form)
        self.save_uploaded_photos(self.object)
        messages.success(self.request, 'Data rumah dinas berhasil disimpan.')
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if getattr(self, 'object', None):
            ctx['foto_rumah_list'] = self.object.galeri_foto.all()
        else:
            ctx['foto_rumah_list'] = []

        return ctx


class RumahDinasCreateView(BMNRequiredMixin, RumahDinasPhotoMixin, CreateView):
    model = RumahDinas
    form_class = RumahDinasForm


class RumahDinasUpdateView(BMNRequiredMixin, RumahDinasPhotoMixin, UpdateView):
    model = RumahDinas
    form_class = RumahDinasForm


@login_required
@require_POST
def rumah_foto_delete(request, pk):
    if not can_manage_master(request.user):
        messages.error(request, 'Anda tidak memiliki hak akses untuk menghapus foto rumah dinas.')
        return redirect('dashboard')

    foto = get_object_or_404(FotoRumahDinas, pk=pk)
    rumah_id = foto.rumah_dinas_id
    foto.foto.delete(save=False)
    foto.delete()

    messages.success(request, 'Foto rumah dinas berhasil dihapus.')
    return redirect('master:rumah_update', pk=rumah_id)
