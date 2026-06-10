from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from core.roles import BMNRequiredMixin
from .models import SIPRumahDinas
from .forms import SIPRumahDinasForm


class SIPRumahDinasListView(BMNRequiredMixin, ListView):
    model = SIPRumahDinas
    template_name = 'rumah_dinas/sip_list.html'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('rumah_dinas', 'pegawai')


class SIPRumahDinasCreateView(BMNRequiredMixin, CreateView):
    model = SIPRumahDinas
    form_class = SIPRumahDinasForm
    template_name = 'rumah_dinas/form.html'
    success_url = reverse_lazy('rumah_dinas:sip_list')

    def form_valid(self, form):
        form.instance.dibuat_oleh = self.request.user
        return super().form_valid(form)


class SIPRumahDinasUpdateView(BMNRequiredMixin, UpdateView):
    model = SIPRumahDinas
    form_class = SIPRumahDinasForm
    template_name = 'rumah_dinas/form.html'
    success_url = reverse_lazy('rumah_dinas:sip_list')