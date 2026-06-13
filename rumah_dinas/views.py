from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models.deletion import ProtectedError
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from core.roles import BMNRequiredMixin
from core.listing import SearchListMixin
from core.detail import GenericDetailMixin
from core.access import UnitScopedQuerysetMixin, UnitScopedFormMixin
from .models import SIPRumahDinas
from .forms import SIPRumahDinasForm


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


class SIPRumahDinasListView(BMNRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    template_name = 'rumah_dinas/sip_list.html'
    select_related = ['rumah_dinas', 'pegawai', 'pegawai__unit_kerja', 'penghuni', 'penghuni__unit_kerja']
    search_fields = [
        ('nomor_sip', 'Nomor SIP'),
        ('rumah_dinas__kode_rumah', 'Kode Rumah'),
        ('rumah_dinas__nama_rumah', 'Nama Rumah'),
        ('rumah_dinas__alamat', 'Alamat Rumah'),
        ('rumah_dinas__kondisi', 'Kondisi Rumah'),
        ('pegawai__nama', 'Nama Pemegang SIP'),
        ('penghuni__nama', 'Nama Penghuni Aktual'),
        ('pegawai__nip', 'NIP Pegawai'),
        ('pegawai__jabatan', 'Jabatan Pegawai'),
        ('pegawai__unit_kerja__nama_unit', 'Unit Kerja Pegawai'),
        ('pejabat_penandatangan', 'Pejabat Penandatangan'),
        ('status', 'Status SIP'),
        ('status_bayar_pnbp', 'Status Bayar PNBP'),
        ('tahun_pnbp', 'Tahun PNBP'),
        ('catatan', 'Catatan'),
    ]


class SIPRumahDinasCreateView(BMNRequiredMixin, UnitScopedFormMixin, CreateView):
    model = SIPRumahDinas
    form_class = SIPRumahDinasForm
    template_name = 'rumah_dinas/form.html'
    success_url = reverse_lazy('rumah_dinas:sip_list')

    def form_valid(self, form):
        form.instance.dibuat_oleh = self.request.user
        return super().form_valid(form)


class SIPRumahDinasUpdateView(BMNRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    form_class = SIPRumahDinasForm
    template_name = 'rumah_dinas/form.html'
    success_url = reverse_lazy('rumah_dinas:sip_list')


class SIPRumahDinasDetailView(BMNRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    detail_title = 'Detail SIP Rumah Negara'
    back_url_name = 'rumah_dinas:sip_list'
    edit_url_name = 'rumah_dinas:sip_update'
    delete_url_name = 'rumah_dinas:sip_delete'


class SIPRumahDinasDeleteView(BMNRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    success_url = reverse_lazy('rumah_dinas:sip_list')
    success_message = 'SIP rumah negara berhasil dihapus.'
