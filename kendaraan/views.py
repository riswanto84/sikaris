from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models.deletion import ProtectedError
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from core.roles import BMNRequiredMixin, MaintenanceRequiredMixin, VehicleViewRequiredMixin
from core.listing import SearchListMixin
from core.detail import GenericDetailMixin
from core.access import UnitScopedQuerysetMixin, UnitScopedFormMixin, scope_queryset_by_user
from master.models import Kendaraan

from .models import (
    SIPKendaraan,
    ServiceKendaraan,
    RiwayatKondisiKendaraan,
    BuktiKuitansiServiceKendaraan,
)

from .forms import (
    SIPKendaraanForm,
    ServiceKendaraanForm,
    RiwayatKondisiKendaraanForm,
)


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


def get_kendaraan_foto_map(user=None):
    """
    Membuat mapping:
    {
        "1": "/media/kendaraan/galeri/foto1.jpg",
        "2": "/media/kendaraan/galeri/foto2.jpg",
    }

    Digunakan oleh JavaScript di service_form.html
    untuk menampilkan foto kendaraan berdasarkan pilihan dropdown.
    """
    kendaraan_foto_map = {}

    kendaraan_qs = Kendaraan.objects.prefetch_related('galeri_foto').all()
    if user is not None:
        kendaraan_qs = scope_queryset_by_user(kendaraan_qs, user, 'kendaraan')
    kendaraan_list = kendaraan_qs

    for kendaraan in kendaraan_list:
        foto_pertama = kendaraan.galeri_foto.first()

        if foto_pertama:
            kendaraan_foto_map[str(kendaraan.id)] = foto_pertama.foto.url

    return kendaraan_foto_map


class SIPKendaraanListView(VehicleViewRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    template_name = 'kendaraan/sip_list.html'
    select_related = ['kendaraan', 'pegawai', 'kendaraan__unit_kerja', 'pegawai__unit_kerja']
    search_fields = [
        ('nomor_sip', 'Nomor SIP'),
        ('kendaraan__kode_kendaraan', 'Kode Kendaraan'),
        ('kendaraan__nomor_polisi', 'Nomor Polisi'),
        ('kendaraan__merek', 'Merek Kendaraan'),
        ('kendaraan__tipe', 'Tipe Kendaraan'),
        ('pegawai__nama', 'Nama Pegawai'),
        ('pegawai__nip', 'NIP Pegawai'),
        ('pegawai__jabatan', 'Jabatan Pegawai'),
        ('pegawai__unit_kerja__nama_unit', 'Unit Kerja Pegawai'),
        ('jenis_pemakaian', 'Jenis Pemakaian'),
        ('tujuan_pemakaian', 'Tujuan Pemakaian'),
        ('lokasi_penggunaan', 'Lokasi Penggunaan'),
        ('pejabat_penandatangan', 'Pejabat Penandatangan'),
        ('status', 'Status SIP'),
        ('catatan', 'Catatan'),
    ]


class SIPKendaraanCreateView(BMNRequiredMixin, UnitScopedFormMixin, CreateView):
    model = SIPKendaraan
    form_class = SIPKendaraanForm
    template_name = 'kendaraan/sip_form.html'
    success_url = reverse_lazy('kendaraan:sip_list')

    def form_valid(self, form):
        form.instance.dibuat_oleh = self.request.user
        return super().form_valid(form)


class SIPKendaraanUpdateView(BMNRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    form_class = SIPKendaraanForm
    template_name = 'kendaraan/sip_form.html'
    success_url = reverse_lazy('kendaraan:sip_list')


class SIPKendaraanDetailView(VehicleViewRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    detail_title = 'Detail SIP Kendaraan'
    back_url_name = 'kendaraan:sip_list'
    edit_url_name = 'kendaraan:sip_update'
    delete_url_name = 'kendaraan:sip_delete'


class SIPKendaraanDeleteView(BMNRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    success_url = reverse_lazy('kendaraan:sip_list')
    success_message = 'SIP kendaraan berhasil dihapus.'


class ServiceKendaraanListView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'service_kendaraan'
    model = ServiceKendaraan
    template_name = 'kendaraan/service_list.html'
    select_related = ['kendaraan', 'kendaraan__unit_kerja', 'dicatat_oleh']
    search_fields = [
        ('kendaraan__kode_kendaraan', 'Kode Kendaraan'),
        ('kendaraan__nomor_polisi', 'Nomor Polisi'),
        ('kendaraan__merek', 'Merek Kendaraan'),
        ('kendaraan__tipe', 'Tipe Kendaraan'),
        ('kendaraan__unit_kerja__nama_unit', 'Unit Kerja'),
        ('jenis_service', 'Jenis Service'),
        ('bengkel', 'Bengkel'),
        ('uraian_pekerjaan', 'Uraian Pekerjaan'),
        ('sparepart_diganti', 'Sparepart Diganti'),
        ('kondisi_sebelum', 'Kondisi Sebelum'),
        ('kondisi_sesudah', 'Kondisi Sesudah'),
        ('dicatat_oleh__username', 'Petugas Pencatat'),
    ]


class ServiceKendaraanCreateView(MaintenanceRequiredMixin, UnitScopedFormMixin, CreateView):
    model = ServiceKendaraan
    form_class = ServiceKendaraanForm
    template_name = 'kendaraan/service_form.html'
    success_url = reverse_lazy('kendaraan:service_list')

    def form_valid(self, form):
        form.instance.dicatat_oleh = self.request.user

        response = super().form_valid(form)

        for file in self.request.FILES.getlist('kuitansi_files'):
            BuktiKuitansiServiceKendaraan.objects.create(
                service=self.object,
                file=file,
                diupload_oleh=self.request.user
            )

        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['kendaraan_foto_map'] = get_kendaraan_foto_map(self.request.user)
        ctx['foto_kendaraan_aktif'] = None
        ctx['kuitansi_list'] = []

        return ctx


class ServiceKendaraanDetailView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'service_kendaraan'
    model = ServiceKendaraan
    detail_title = 'Detail Service Kendaraan'
    back_url_name = 'kendaraan:service_list'
    edit_url_name = 'kendaraan:service_update'
    delete_url_name = 'kendaraan:service_delete'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['service_kuitansi_list'] = self.object.bukti_kuitansi.all()
        return ctx


class ServiceKendaraanUpdateView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'service_kendaraan'
    model = ServiceKendaraan
    form_class = ServiceKendaraanForm
    template_name = 'kendaraan/service_form.html'
    success_url = reverse_lazy('kendaraan:service_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        for file in self.request.FILES.getlist('kuitansi_files'):
            BuktiKuitansiServiceKendaraan.objects.create(
                service=self.object,
                file=file,
                diupload_oleh=self.request.user
            )

        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['kendaraan_foto_map'] = get_kendaraan_foto_map(self.request.user)

        if self.object and self.object.kendaraan:
            foto_pertama = self.object.kendaraan.galeri_foto.first()
            ctx['foto_kendaraan_aktif'] = foto_pertama.foto.url if foto_pertama else None
        else:
            ctx['foto_kendaraan_aktif'] = None

        ctx['kuitansi_list'] = self.object.bukti_kuitansi.all()

        return ctx


class ServiceKendaraanDeleteView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'service_kendaraan'
    model = ServiceKendaraan
    success_url = reverse_lazy('kendaraan:service_list')
    success_message = 'Service kendaraan berhasil dihapus.'


@login_required
@require_POST
def kuitansi_service_delete(request, pk):
    kuitansi = get_object_or_404(BuktiKuitansiServiceKendaraan.objects.filter(service__in=scope_queryset_by_user(ServiceKendaraan.objects.all(), request.user, 'service_kendaraan')), pk=pk)
    service_id = kuitansi.service_id

    kuitansi.file.delete(save=False)
    kuitansi.delete()

    return redirect('kendaraan:service_update', pk=service_id)


class RiwayatKondisiListView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'kondisi_kendaraan'
    model = RiwayatKondisiKendaraan
    template_name = 'kendaraan/kondisi_list.html'
    select_related = ['kendaraan', 'kendaraan__unit_kerja', 'dicatat_oleh']
    search_fields = [
        ('kendaraan__kode_kendaraan', 'Kode Kendaraan'),
        ('kendaraan__nomor_polisi', 'Nomor Polisi'),
        ('kendaraan__merek', 'Merek Kendaraan'),
        ('kendaraan__tipe', 'Tipe Kendaraan'),
        ('kendaraan__unit_kerja__nama_unit', 'Unit Kerja'),
        ('kondisi', 'Kondisi'),
        ('uraian_kondisi', 'Uraian Kondisi'),
        ('dicatat_oleh__username', 'Petugas Pencatat'),
    ]


class RiwayatKondisiCreateView(MaintenanceRequiredMixin, UnitScopedFormMixin, CreateView):
    model = RiwayatKondisiKendaraan
    form_class = RiwayatKondisiKendaraanForm
    template_name = 'kendaraan/form.html'
    success_url = reverse_lazy('kendaraan:kondisi_list')

    def form_valid(self, form):
        form.instance.dicatat_oleh = self.request.user
        return super().form_valid(form)

class RiwayatKondisiDetailView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'kondisi_kendaraan'
    model = RiwayatKondisiKendaraan
    detail_title = 'Detail Riwayat Kondisi Kendaraan'
    back_url_name = 'kendaraan:kondisi_list'
    delete_url_name = 'kendaraan:kondisi_delete'


class RiwayatKondisiDeleteView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'kondisi_kendaraan'
    model = RiwayatKondisiKendaraan
    success_url = reverse_lazy('kendaraan:kondisi_list')
    success_message = 'Riwayat kondisi kendaraan berhasil dihapus.'
