from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.db import OperationalError, ProgrammingError
from django.urls import reverse
from django.utils import timezone

from core.access import get_user_unit_kerja, is_biro_umum_user, scope_queryset_by_user
from core.roles import is_admin_system


NOTIF_LIMIT = 12
SIP_REMINDER_DAYS = 30


def _can_see_all(user):
    return bool(user and user.is_authenticated and (is_admin_system(user) or is_biro_umum_user(user)))


def _safe_count(qs):
    try:
        return qs.count()
    except Exception:
        return 0


def _fmt_date(value):
    if not value:
        return '-'
    try:
        return value.strftime('%d-%m-%Y')
    except Exception:
        return str(value)


def _append_item(items, *, title, description, url, level='info', icon='🔔'):
    if len(items) >= NOTIF_LIMIT:
        return
    items.append({
        'title': title,
        'description': description,
        'url': url,
        'level': level,
        'icon': icon,
    })


def _scoped_penghapusan_qs(user):
    from penghapusan.models import PermohonanPenghapusanBMN

    qs = PermohonanPenghapusanBMN.objects.select_related('unit_kerja', 'pemohon')
    if _can_see_all(user):
        return qs
    unit = get_user_unit_kerja(user)
    if not unit:
        return qs.none()
    return qs.filter(unit_kerja=unit)


def _scoped_psp_qs(user):
    from psp.models import PermohonanPSPBMN

    qs = PermohonanPSPBMN.objects.select_related('unit_kerja', 'pemohon')
    if _can_see_all(user):
        return qs
    unit = get_user_unit_kerja(user)
    if not unit:
        return qs.none()
    return qs.filter(unit_kerja=unit)


def _scoped_sip_kendaraan_qs(user):
    from kendaraan.models import SIPKendaraan

    qs = SIPKendaraan.objects.select_related('kendaraan', 'pegawai', 'kendaraan__unit_kerja', 'pegawai__unit_kerja')
    if _can_see_all(user):
        return qs
    try:
        return scope_queryset_by_user(qs, user, 'sip_kendaraan')
    except PermissionDenied:
        return qs.none()


def _scoped_sip_rumah_qs(user):
    from rumah_dinas.models import SIPRumahDinas

    qs = SIPRumahDinas.objects.select_related('rumah_dinas', 'pegawai', 'penghuni', 'rumah_dinas__unit_kerja', 'pegawai__unit_kerja')
    if _can_see_all(user):
        return qs
    try:
        return scope_queryset_by_user(qs, user, 'sip_rumah')
    except PermissionDenied:
        return qs.none()


def build_notifications(user):
    """Bangun daftar notifikasi topbar.

    Notifikasi aktif meliputi:
    - Usulan Penghapusan BMN dari satker untuk Biro Umum/Admin System.
    - Usulan PSP BMN dari satker untuk Biro Umum/Admin System.
    - Usulan yang perlu perbaikan untuk pemohon/satker.
    - SIP kendaraan/rumah negara yang sudah habis atau akan habis masa berlakunya.
    """
    default = {
        'notification_count': 0,
        'notification_items': [],
        'notification_has_more': False,
    }
    if not user or not user.is_authenticated:
        return default

    try:
        today = timezone.localdate()
        soon = today + timedelta(days=SIP_REMINDER_DAYS)
        items = []
        total = 0
        can_see_all = _can_see_all(user)

        penghapusan_qs = _scoped_penghapusan_qs(user)
        psp_qs = _scoped_psp_qs(user)

        if can_see_all:
            penghapusan_baru = penghapusan_qs.filter(status='DIAJUKAN')
            psp_baru = psp_qs.filter(status='DIAJUKAN')
            total += _safe_count(penghapusan_baru) + _safe_count(psp_baru)

            for obj in penghapusan_baru.order_by('-tanggal_permohonan', '-created_at')[:4]:
                _append_item(
                    items,
                    title='Usulan penghapusan BMN baru',
                    description=f'{obj.nomor_permohonan or "Tanpa nomor"} dari {obj.unit_kerja or "Satker"}',
                    url=reverse('penghapusan:detail', kwargs={'pk': obj.pk}),
                    level='warning',
                    icon='🗑️',
                )
            for obj in psp_baru.order_by('-tanggal_permohonan', '-created_at')[:4]:
                _append_item(
                    items,
                    title='Usulan PSP BMN baru',
                    description=f'{obj.nomor_permohonan or "Tanpa nomor"} dari {obj.unit_kerja or "Satker"}',
                    url=reverse('psp:detail', kwargs={'pk': obj.pk}),
                    level='warning',
                    icon='✅',
                )
        else:
            penghapusan_perbaikan = penghapusan_qs.filter(status='PERLU_PERBAIKAN')
            psp_perbaikan = psp_qs.filter(status='PERLU_PERBAIKAN')
            total += _safe_count(penghapusan_perbaikan) + _safe_count(psp_perbaikan)

            for obj in penghapusan_perbaikan.order_by('-tanggal_permohonan', '-created_at')[:3]:
                _append_item(
                    items,
                    title='Perbaikan usulan penghapusan BMN',
                    description=f'{obj.nomor_permohonan or "Tanpa nomor"} perlu dilengkapi',
                    url=reverse('penghapusan:detail', kwargs={'pk': obj.pk}),
                    level='danger',
                    icon='📝',
                )
            for obj in psp_perbaikan.order_by('-tanggal_permohonan', '-created_at')[:3]:
                _append_item(
                    items,
                    title='Perbaikan usulan PSP BMN',
                    description=f'{obj.nomor_permohonan or "Tanpa nomor"} perlu dilengkapi',
                    url=reverse('psp:detail', kwargs={'pk': obj.pk}),
                    level='danger',
                    icon='📝',
                )

        sip_kendaraan_qs = _scoped_sip_kendaraan_qs(user).filter(status='AKTIF')
        sip_rumah_qs = _scoped_sip_rumah_qs(user).filter(status='AKTIF')

        sip_kendaraan_habis = sip_kendaraan_qs.filter(tanggal_akhir__lt=today)
        sip_rumah_habis = sip_rumah_qs.filter(tanggal_akhir__lt=today)
        sip_kendaraan_akan_habis = sip_kendaraan_qs.filter(tanggal_akhir__range=[today, soon])
        sip_rumah_akan_habis = sip_rumah_qs.filter(tanggal_akhir__range=[today, soon])

        total += (
            _safe_count(sip_kendaraan_habis)
            + _safe_count(sip_rumah_habis)
            + _safe_count(sip_kendaraan_akan_habis)
            + _safe_count(sip_rumah_akan_habis)
        )

        for obj in sip_kendaraan_habis.order_by('tanggal_akhir')[:3]:
            _append_item(
                items,
                title='SIP kendaraan sudah habis',
                description=f'{obj.nomor_sip} berakhir {_fmt_date(obj.tanggal_akhir)}',
                url=reverse('kendaraan:sip_detail', kwargs={'pk': obj.pk}),
                level='danger',
                icon='🚘',
            )
        for obj in sip_rumah_habis.order_by('tanggal_akhir')[:3]:
            _append_item(
                items,
                title='SIP rumah negara sudah habis',
                description=f'{obj.nomor_sip} berakhir {_fmt_date(obj.tanggal_akhir)}',
                url=reverse('rumah_dinas:sip_detail', kwargs={'pk': obj.pk}),
                level='danger',
                icon='🏠',
            )
        for obj in sip_kendaraan_akan_habis.order_by('tanggal_akhir')[:3]:
            _append_item(
                items,
                title='SIP kendaraan akan habis',
                description=f'{obj.nomor_sip} berakhir {_fmt_date(obj.tanggal_akhir)}',
                url=reverse('kendaraan:sip_detail', kwargs={'pk': obj.pk}),
                level='warning',
                icon='🚘',
            )
        for obj in sip_rumah_akan_habis.order_by('tanggal_akhir')[:3]:
            _append_item(
                items,
                title='SIP rumah negara akan habis',
                description=f'{obj.nomor_sip} berakhir {_fmt_date(obj.tanggal_akhir)}',
                url=reverse('rumah_dinas:sip_detail', kwargs={'pk': obj.pk}),
                level='warning',
                icon='🏠',
            )

        return {
            'notification_count': total,
            'notification_items': items,
            'notification_has_more': total > len(items),
        }
    except (OperationalError, ProgrammingError):
        return default
    except Exception:
        # Notifikasi tidak boleh membuat halaman utama gagal dibuka.
        return default
