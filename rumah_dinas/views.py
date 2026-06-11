from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from core.roles import BMNRequiredMixin
from core.listing import SearchListMixin
from core.access import UnitScopedQuerysetMixin, UnitScopedFormMixin
from .models import SIPRumahDinas
from .forms import SIPRumahDinasForm


class SIPRumahDinasListView(BMNRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    template_name = 'rumah_dinas/sip_list.html'
    select_related = ['rumah_dinas', 'pegawai', 'pegawai__unit_kerja']
    search_fields = [
        ('nomor_sip', 'Nomor SIP'),
        ('rumah_dinas__kode_rumah', 'Kode Rumah'),
        ('rumah_dinas__nama_rumah', 'Nama Rumah'),
        ('rumah_dinas__alamat', 'Alamat Rumah'),
        ('rumah_dinas__kondisi', 'Kondisi Rumah'),
        ('pegawai__nama', 'Nama Pegawai/Penghuni'),
        ('pegawai__nip', 'NIP Pegawai'),
        ('pegawai__jabatan', 'Jabatan Pegawai'),
        ('pegawai__unit_kerja__nama_unit', 'Unit Kerja Pegawai'),
        ('pejabat_penandatangan', 'Pejabat Penandatangan'),
        ('status', 'Status SIP'),
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
