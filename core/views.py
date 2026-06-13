from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum

from master.models import Kendaraan, RumahDinas, Pegawai, UnitKerja
from kendaraan.models import SIPKendaraan, ServiceKendaraan
from rumah_dinas.models import SIPRumahDinas, PerbaikanRumahDinas
from core.access import scope_queryset_by_user, is_biro_umum_user, get_user_unit_kerja


def _scoped_dashboard_querysets(user):
    """Queryset dashboard yang mengikuti hak akses unit kerja user.

    - Biro Umum/superuser melihat seluruh satker.
    - User unit kerja hanya melihat data sesuai Unit Kerja/Satker pada Manajemen User.
    """
    kendaraan_qs = scope_queryset_by_user(
        Kendaraan.objects.select_related('unit_kerja', 'pengguna'),
        user,
        'kendaraan',
    )
    pegawai_qs = scope_queryset_by_user(
        Pegawai.objects.select_related('unit_kerja'),
        user,
        'pegawai',
    )
    unit_qs = scope_queryset_by_user(
        UnitKerja.objects.all(),
        user,
        'unit',
    )
    rumah_qs = scope_queryset_by_user(
        RumahDinas.objects.all(),
        user,
        'rumah',
    )
    sip_kendaraan_qs = scope_queryset_by_user(
        SIPKendaraan.objects.select_related('kendaraan', 'pegawai', 'pegawai__unit_kerja'),
        user,
        'sip_kendaraan',
    )
    sip_rumah_qs = scope_queryset_by_user(
        SIPRumahDinas.objects.select_related('rumah_dinas', 'pegawai', 'pegawai__unit_kerja'),
        user,
        'sip_rumah',
    )
    service_qs = scope_queryset_by_user(
        ServiceKendaraan.objects.select_related('kendaraan', 'kendaraan__unit_kerja'),
        user,
        'service_kendaraan',
    )
    perbaikan_qs = scope_queryset_by_user(
        PerbaikanRumahDinas.objects.select_related('rumah_dinas', 'pelapor', 'pelapor__unit_kerja'),
        user,
        'perbaikan_rumah',
    )

    return {
        'kendaraan': kendaraan_qs,
        'pegawai': pegawai_qs,
        'unit': unit_qs,
        'rumah': rumah_qs,
        'sip_kendaraan': sip_kendaraan_qs,
        'sip_rumah': sip_rumah_qs,
        'service': service_qs,
        'perbaikan': perbaikan_qs,
    }


def dashboard_stats(user):
    today = timezone.localdate()
    soon = today + timedelta(days=30)
    qs = _scoped_dashboard_querysets(user)

    service_bulan_ini_qs = qs['service'].filter(
        tanggal_service__month=today.month,
        tanggal_service__year=today.year,
    )

    return {
        'total_kendaraan': qs['kendaraan'].count(),
        'kendaraan_baik': qs['kendaraan'].filter(kondisi='BAIK').count(),
        'kendaraan_rusak_ringan': qs['kendaraan'].filter(kondisi='RUSAK_RINGAN').count(),
        'kendaraan_rusak_berat': qs['kendaraan'].filter(kondisi='RUSAK_BERAT').count(),

        'total_rumah': qs['rumah'].count(),
        'rumah_baik': qs['rumah'].filter(kondisi='BAIK').count(),
        'rumah_rusak_ringan': qs['rumah'].filter(kondisi='RUSAK_RINGAN').count(),
        'rumah_rusak_berat': qs['rumah'].filter(kondisi='RUSAK_BERAT').count(),

        'total_pegawai': qs['pegawai'].count(),
        'total_unit_kerja': qs['unit'].count(),

        'sip_kendaraan_aktif': qs['sip_kendaraan'].filter(status='AKTIF').count(),
        'sip_rumah_aktif': qs['sip_rumah'].filter(status='AKTIF').count(),
        'sip_kendaraan_akan_berakhir': qs['sip_kendaraan'].filter(
            status='AKTIF',
            tanggal_akhir__range=[today, soon],
        ).count(),
        'sip_rumah_akan_berakhir': qs['sip_rumah'].filter(
            status='AKTIF',
            tanggal_akhir__range=[today, soon],
        ).count(),

        'service_bulan_ini': service_bulan_ini_qs.count(),
        'service_bulan_ini_biaya': service_bulan_ini_qs.aggregate(total=Sum('total_biaya')).get('total') or 0,
        'perbaikan_rumah': qs['perbaikan'].count(),
    }


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = _scoped_dashboard_querysets(self.request.user)
        today = timezone.localdate()
        soon = today + timedelta(days=30)
        user_unit = get_user_unit_kerja(self.request.user)

        ctx.update(dashboard_stats(self.request.user))
        ctx.update({
            'dashboard_scope_label': 'Semua Satker / Unit Kerja' if is_biro_umum_user(self.request.user) else (user_unit.nama_unit if user_unit else 'Unit kerja belum diatur'),
            'service_terakhir': qs['service'].order_by('-tanggal_service', '-created_at')[:5],
            'kendaraan_terbaru': qs['kendaraan'].exclude(kondisi='BAIK').order_by('kondisi', 'nomor_polisi')[:5],
            'sip_akan_berakhir': qs['sip_kendaraan'].filter(
                status='AKTIF',
                tanggal_akhir__range=[today, soon],
            ).order_by('tanggal_akhir')[:5],
            'sip_rumah_akan_berakhir_list': qs['sip_rumah'].filter(
                status='AKTIF',
                tanggal_akhir__range=[today, soon],
            ).order_by('tanggal_akhir')[:5],
        })
        return ctx


@login_required
def dashboard_stats_api(request):
    return JsonResponse(dashboard_stats(request.user))
