from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.utils import timezone
from master.models import Kendaraan, RumahDinas, Pegawai, UnitKerja
from kendaraan.models import SIPKendaraan, ServiceKendaraan
from rumah_dinas.models import SIPRumahDinas, PerbaikanRumahDinas


def dashboard_stats():
    today = timezone.localdate()
    soon = today + timedelta(days=30)
    return {
        'total_kendaraan': Kendaraan.objects.count(),
        'kendaraan_baik': Kendaraan.objects.filter(kondisi='BAIK').count(),
        'kendaraan_rusak_ringan': Kendaraan.objects.filter(kondisi='RUSAK_RINGAN').count(),
        'kendaraan_rusak_berat': Kendaraan.objects.filter(kondisi='RUSAK_BERAT').count(),
        'total_rumah': RumahDinas.objects.count(),
        'rumah_baik': RumahDinas.objects.filter(kondisi='BAIK').count(),
        'rumah_rusak_ringan': RumahDinas.objects.filter(kondisi='RUSAK_RINGAN').count(),
        'rumah_rusak_berat': RumahDinas.objects.filter(kondisi='RUSAK_BERAT').count(),
        'total_pegawai': Pegawai.objects.count(),
        'total_unit_kerja': UnitKerja.objects.count(),
        'sip_kendaraan_aktif': SIPKendaraan.objects.filter(status='AKTIF').count(),
        'sip_rumah_aktif': SIPRumahDinas.objects.filter(status='AKTIF').count(),
        'sip_kendaraan_akan_berakhir': SIPKendaraan.objects.filter(status='AKTIF', tanggal_akhir__range=[today, soon]).count(),
        'sip_rumah_akan_berakhir': SIPRumahDinas.objects.filter(status='AKTIF', tanggal_akhir__range=[today, soon]).count(),
        'service_bulan_ini': ServiceKendaraan.objects.filter(tanggal_service__month=today.month, tanggal_service__year=today.year).count(),
        'perbaikan_rumah': PerbaikanRumahDinas.objects.count(),
    }


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(dashboard_stats())
        ctx.update({
            'service_terakhir': ServiceKendaraan.objects.select_related('kendaraan').all()[:5],
            'kendaraan_terbaru': Kendaraan.objects.select_related('unit_kerja').all()[:5],
            'sip_akan_berakhir': SIPKendaraan.objects.select_related('kendaraan', 'pegawai').filter(status='AKTIF').order_by('tanggal_akhir')[:5],
        })
        return ctx


@login_required
def dashboard_stats_api(request):
    return JsonResponse(dashboard_stats())
