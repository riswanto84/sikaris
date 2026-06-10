from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from core.roles import BMNRequiredMixin, VehicleViewRequiredMixin, can_manage_master
from core.listing import SearchListMixin
from .models import (
    UnitKerja,
    Pegawai,
    Kendaraan,
    RumahDinas,
    FotoKendaraan,
    FotoRumahDinas,
)
from .forms import UnitKerjaForm, PegawaiForm, KendaraanForm, RumahDinasForm


class UnitKerjaListView(BMNRequiredMixin, SearchListMixin):
    model = UnitKerja
    template_name = 'master/unitkerja_list.html'
    search_fields = [
        ('nama_unit', 'Nama Unit Kerja'),
        ('keterangan', 'Keterangan'),
    ]


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
    select_related = ['unit_kerja']
    search_fields = [
        ('nip', 'NIP'),
        ('nik', 'NIK'),
        ('nama', 'Nama Pegawai'),
        ('jabatan', 'Jabatan'),
        ('pangkat', 'Pangkat'),
        ('golongan', 'Golongan'),
        ('unit_kerja__nama_unit', 'Unit Kerja'),
        ('no_hp', 'No HP'),
        ('email', 'Email'),
        ('status_pegawai', 'Status Pegawai'),
    ]


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
    select_related = ['unit_kerja', 'pengguna']
    search_fields = [
        ('kode_kendaraan', 'Kode Kendaraan'),
        ('nomor_polisi', 'Nomor Polisi'),
        ('merek', 'Merek'),
        ('tipe', 'Tipe'),
        ('jenis_kendaraan', 'Jenis Kendaraan'),
        ('warna', 'Warna'),
        ('nomor_rangka', 'Nomor Rangka'),
        ('nomor_mesin', 'Nomor Mesin'),
        ('nomor_bpkb', 'Nomor BPKB'),
        ('nomor_stnk', 'Nomor STNK'),
        ('nup', 'NUP'),
        ('kode_barang', 'Kode Barang'),
        ('unit_kerja__nama_unit', 'Unit Kerja'),
        ('pengguna__nama', 'Nama Pengguna'),
        ('pengguna__nip', 'NIP Pengguna'),
        ('kondisi', 'Kondisi'),
        ('status_pemanfaatan', 'Status Pemanfaatan'),
    ]


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
    search_fields = [
        ('kode_rumah', 'Kode Rumah'),
        ('nama_rumah', 'Nama Rumah'),
        ('jenis_rumah', 'Jenis Rumah'),
        ('alamat', 'Alamat'),
        ('provinsi', 'Provinsi'),
        ('kabupaten_kota', 'Kabupaten/Kota'),
        ('kecamatan', 'Kecamatan'),
        ('kelurahan', 'Kelurahan'),
        ('nup', 'NUP'),
        ('kode_barang', 'Kode Barang'),
        ('nomor_sertifikat', 'Nomor Sertifikat'),
        ('status_tanah', 'Status Tanah'),
        ('kondisi', 'Kondisi'),
        ('status_pemanfaatan', 'Status Pemanfaatan'),
    ]


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
