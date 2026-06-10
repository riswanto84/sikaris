from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView

from core.roles import BMNRequiredMixin, MaintenanceRequiredMixin, VehicleViewRequiredMixin
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


def get_kendaraan_foto_map():
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

    kendaraan_list = Kendaraan.objects.prefetch_related('galeri_foto').all()

    for kendaraan in kendaraan_list:
        foto_pertama = kendaraan.galeri_foto.first()

        if foto_pertama:
            kendaraan_foto_map[str(kendaraan.id)] = foto_pertama.foto.url

    return kendaraan_foto_map


class SIPKendaraanListView(VehicleViewRequiredMixin, ListView):
    model = SIPKendaraan
    template_name = 'kendaraan/sip_list.html'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('kendaraan', 'pegawai')

        q = self.request.GET.get('q')

        if q:
            qs = qs.filter(nomor_sip__icontains=q)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class SIPKendaraanCreateView(BMNRequiredMixin, CreateView):
    model = SIPKendaraan
    form_class = SIPKendaraanForm
    template_name = 'kendaraan/sip_form.html'
    success_url = reverse_lazy('kendaraan:sip_list')

    def form_valid(self, form):
        form.instance.dibuat_oleh = self.request.user
        return super().form_valid(form)


class SIPKendaraanUpdateView(BMNRequiredMixin, UpdateView):
    model = SIPKendaraan
    form_class = SIPKendaraanForm
    template_name = 'kendaraan/sip_form.html'
    success_url = reverse_lazy('kendaraan:sip_list')


class ServiceKendaraanListView(MaintenanceRequiredMixin, ListView):
    model = ServiceKendaraan
    template_name = 'kendaraan/service_list.html'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('kendaraan')


class ServiceKendaraanCreateView(MaintenanceRequiredMixin, CreateView):
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

        ctx['kendaraan_foto_map'] = get_kendaraan_foto_map()
        ctx['foto_kendaraan_aktif'] = None
        ctx['kuitansi_list'] = []

        return ctx


class ServiceKendaraanUpdateView(MaintenanceRequiredMixin, UpdateView):
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

        ctx['kendaraan_foto_map'] = get_kendaraan_foto_map()

        if self.object and self.object.kendaraan:
            foto_pertama = self.object.kendaraan.galeri_foto.first()
            ctx['foto_kendaraan_aktif'] = foto_pertama.foto.url if foto_pertama else None
        else:
            ctx['foto_kendaraan_aktif'] = None

        ctx['kuitansi_list'] = self.object.bukti_kuitansi.all()

        return ctx


@login_required
@require_POST
def kuitansi_service_delete(request, pk):
    kuitansi = get_object_or_404(BuktiKuitansiServiceKendaraan, pk=pk)
    service_id = kuitansi.service_id

    kuitansi.file.delete(save=False)
    kuitansi.delete()

    return redirect('kendaraan:service_update', pk=service_id)


class RiwayatKondisiListView(MaintenanceRequiredMixin, ListView):
    model = RiwayatKondisiKendaraan
    template_name = 'kendaraan/kondisi_list.html'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('kendaraan')


class RiwayatKondisiCreateView(MaintenanceRequiredMixin, CreateView):
    model = RiwayatKondisiKendaraan
    form_class = RiwayatKondisiKendaraanForm
    template_name = 'kendaraan/form.html'
    success_url = reverse_lazy('kendaraan:kondisi_list')

    def form_valid(self, form):
        form.instance.dicatat_oleh = self.request.user
        return super().form_valid(form)