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
from psp.models import PermohonanPSPBMN
from core.access import scope_queryset_by_user, get_user_unit_kerja, get_dashboard_scope_label


KONDISI_BAIK_VALUES = {'BAIK', 'BAIK/TERAWAT', 'BAIK TERAWAT'}
KONDISI_RUSAK_RINGAN_VALUES = {'RUSAK_RINGAN', 'RUSAK RINGAN', 'RINGAN', 'RR'}
KONDISI_RUSAK_BERAT_VALUES = {'RUSAK_BERAT', 'RUSAK BERAT', 'BERAT', 'RB'}


def _normalize_kondisi(value):
    """Normalisasi nilai kondisi agar dashboard tetap benar.

    Beberapa data dummy/import lama tersimpan sebagai label tampilan seperti
    "Baik", "Rusak Ringan", atau "Rusak Berat", sementara choices model
    memakai kode "BAIK", "RUSAK_RINGAN", dan "RUSAK_BERAT".
    Fungsi ini membuat perhitungan dashboard tidak bergantung pada format itu.
    """
    value = (value or '').strip().upper().replace('-', ' ')
    value = ' '.join(value.split())
    if value in KONDISI_BAIK_VALUES:
        return 'BAIK'
    if value in KONDISI_RUSAK_RINGAN_VALUES:
        return 'RUSAK_RINGAN'
    if value in KONDISI_RUSAK_BERAT_VALUES:
        return 'RUSAK_BERAT'
    # Antisipasi variasi lain dari data impor.
    if 'RUSAK' in value and 'RINGAN' in value:
        return 'RUSAK_RINGAN'
    if 'RUSAK' in value and 'BERAT' in value:
        return 'RUSAK_BERAT'
    if 'BAIK' in value:
        return 'BAIK'
    return value


def _condition_counts(qs):
    counts = {'BAIK': 0, 'RUSAK_RINGAN': 0, 'RUSAK_BERAT': 0}
    for kondisi in qs.values_list('kondisi', flat=True):
        key = _normalize_kondisi(kondisi)
        if key in counts:
            counts[key] += 1
    return counts


def _ring_gradient(baik, rusak_ringan, rusak_berat):
    total = baik + rusak_ringan + rusak_berat
    if total <= 0:
        return 'conic-gradient(#e5e7eb 0 100%)'
    p_baik = (baik / total) * 100
    p_rr = p_baik + (rusak_ringan / total) * 100
    return (
        f'conic-gradient(#22c55e 0 {p_baik:.2f}%, '
        f'#f59e0b {p_baik:.2f}% {p_rr:.2f}%, '
        f'#ef4444 {p_rr:.2f}% 100%)'
    )


def _exclude_kondisi_baik(qs):
    # Untuk list "perlu tindakan"; dibuat longgar agar data kode maupun label tetap terfilter.
    return qs.exclude(kondisi__iexact='BAIK').exclude(kondisi__iexact='Baik')


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
    psp_qs = scope_queryset_by_user(
        PermohonanPSPBMN.objects.select_related('unit_kerja', 'pemohon', 'pemohon__unit_kerja'),
        user,
        'psp',
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
        'psp': psp_qs,
    }


def dashboard_stats(user):
    today = timezone.localdate()
    soon = today + timedelta(days=30)
    qs = _scoped_dashboard_querysets(user)

    service_bulan_ini_qs = qs['service'].filter(
        tanggal_service__month=today.month,
        tanggal_service__year=today.year,
    )

    kendaraan_counts = _condition_counts(qs['kendaraan'])
    rumah_counts = _condition_counts(qs['rumah'])

    psp_proses_statuses = [
        'VALIDASI_DATA', 'DIAJUKAN', 'DIVERIFIKASI_BIRO', 'SIAP_DIAJUKAN_SEKJEN',
        'DIAJUKAN_SEKJEN', 'DISETUJUI_SEKJEN', 'DIAJUKAN_BIRO_HUKUM',
        'REVISI_DRAFT_SK', 'DISETUJUI', 'PROSES_PSP',
    ]
    psp_selesai_statuses = ['SK_TERBIT', 'SELESAI']
    psp_perlu_tindak_lanjut_statuses = ['DIAJUKAN', 'VALIDASI_DATA', 'PERLU_PERBAIKAN', 'REVISI_DRAFT_SK']

    return {
        'total_kendaraan': qs['kendaraan'].count(),
        'kendaraan_baik': kendaraan_counts['BAIK'],
        'kendaraan_rusak_ringan': kendaraan_counts['RUSAK_RINGAN'],
        'kendaraan_rusak_berat': kendaraan_counts['RUSAK_BERAT'],
        'kendaraan_ring_gradient': _ring_gradient(
            kendaraan_counts['BAIK'],
            kendaraan_counts['RUSAK_RINGAN'],
            kendaraan_counts['RUSAK_BERAT'],
        ),

        'total_rumah': qs['rumah'].count(),
        'rumah_baik': rumah_counts['BAIK'],
        'rumah_rusak_ringan': rumah_counts['RUSAK_RINGAN'],
        'rumah_rusak_berat': rumah_counts['RUSAK_BERAT'],
        'rumah_ring_gradient': _ring_gradient(
            rumah_counts['BAIK'],
            rumah_counts['RUSAK_RINGAN'],
            rumah_counts['RUSAK_BERAT'],
        ),

        'total_pegawai': qs['pegawai'].count(),
        'total_unit_kerja': qs['unit'].count(),

        # Ringkasan permohonan SIP sesuai scope kewenangan role.
        # Pengelola BMN melihat unit/eselon I kewenangannya, sedangkan
        # pejabat penerbit SIP melihat pengajuan sesuai unit yang menjadi kewenangannya.
        'total_sip_kendaraan': qs['sip_kendaraan'].count(),
        'sip_kendaraan_draft': qs['sip_kendaraan'].filter(status='DRAFT').count(),
        'sip_kendaraan_ditolak': qs['sip_kendaraan'].filter(status='DITOLAK').count(),
        'sip_kendaraan_terbit': qs['sip_kendaraan'].filter(status__in=['TERBIT', 'AKTIF']).count(),
        'sip_kendaraan_aktif': qs['sip_kendaraan'].filter(status__in=['TERBIT', 'AKTIF']).count(),

        'total_sip_rumah': qs['sip_rumah'].count(),
        'sip_rumah_draft': qs['sip_rumah'].filter(status='DRAFT').count(),
        'sip_rumah_ditolak': qs['sip_rumah'].filter(status='DITOLAK').count(),
        'sip_rumah_terbit': qs['sip_rumah'].filter(status__in=['TERBIT', 'AKTIF']).count(),
        'sip_rumah_aktif': qs['sip_rumah'].filter(status__in=['TERBIT', 'AKTIF']).count(),
        'sip_kendaraan_akan_berakhir': qs['sip_kendaraan'].filter(
            status__in=['TERBIT', 'AKTIF'],
            tanggal_akhir__range=[today, soon],
        ).count(),
        'sip_rumah_akan_berakhir': qs['sip_rumah'].filter(
            status__in=['TERBIT', 'AKTIF'],
            tanggal_akhir__range=[today, soon],
        ).count(),

        'service_bulan_ini': service_bulan_ini_qs.count(),
        'service_bulan_ini_biaya': service_bulan_ini_qs.aggregate(total=Sum('total_biaya')).get('total') or 0,
        'perbaikan_rumah': qs['perbaikan'].count(),

        # Ringkasan PSP BMN sesuai scope kewenangan role.
        'total_psp': qs['psp'].count(),
        'psp_diajukan': qs['psp'].filter(status='DIAJUKAN').count(),
        'psp_validasi': qs['psp'].filter(status='VALIDASI_DATA').count(),
        'psp_perlu_perbaikan': qs['psp'].filter(status='PERLU_PERBAIKAN').count(),
        'psp_proses': qs['psp'].filter(status__in=psp_proses_statuses).count(),
        'psp_selesai': qs['psp'].filter(status__in=psp_selesai_statuses).count(),
        'psp_perlu_tindak_lanjut': qs['psp'].filter(status__in=psp_perlu_tindak_lanjut_statuses).count(),
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
            'dashboard_scope_label': get_dashboard_scope_label(self.request.user),
            'service_terakhir': qs['service'].order_by('-tanggal_service', '-created_at')[:5],
            'kendaraan_terbaru': _exclude_kondisi_baik(qs['kendaraan']).order_by('kondisi', 'nomor_polisi')[:5],
            'rumah_perlu_tindakan': _exclude_kondisi_baik(qs['rumah']).order_by('kondisi', 'kode_rumah')[:5],
            'sip_akan_berakhir': qs['sip_kendaraan'].filter(
                status__in=['TERBIT', 'AKTIF'],
                tanggal_akhir__range=[today, soon],
            ).order_by('tanggal_akhir')[:5],
            'sip_rumah_akan_berakhir_list': qs['sip_rumah'].filter(
                status__in=['TERBIT', 'AKTIF'],
                tanggal_akhir__range=[today, soon],
            ).order_by('tanggal_akhir')[:5],
            'psp_terbaru': qs['psp'].order_by('-tanggal_permohonan', '-created_at')[:5],
            'psp_perlu_tindak_lanjut_list': qs['psp'].filter(
                status__in=['DIAJUKAN', 'VALIDASI_DATA', 'PERLU_PERBAIKAN', 'REVISI_DRAFT_SK']
            ).order_by('tanggal_permohonan', 'created_at')[:5],
        })
        return ctx


@login_required
def dashboard_stats_api(request):
    return JsonResponse(dashboard_stats(request.user))
