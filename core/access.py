from django.core.exceptions import PermissionDenied
from django.db.models import Q

from master.models import Pegawai, UnitKerja

BIRO_UMUM_GROUP = 'Biro Umum'
BIRO_UMUM_KEYWORD = 'BIRO UMUM'


def _norm(value):
    return (value or '').strip().upper()


def is_biro_umum_user(user):
    """User Biro Umum dapat mengelola seluruh satker/unit kerja."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.groups.filter(name__iexact=BIRO_UMUM_GROUP).exists():
        return True
    profile = getattr(user, 'profile', None)
    profile_unit_name = _norm(getattr(getattr(profile, 'unit_kerja', None), 'nama_unit', ''))
    if BIRO_UMUM_KEYWORD in profile_unit_name:
        return True
    pegawai = get_user_pegawai(user)
    unit_name = _norm(getattr(getattr(pegawai, 'unit_kerja', None), 'nama_unit', ''))
    return BIRO_UMUM_KEYWORD in unit_name


def get_user_pegawai(user):
    """Cari data pegawai milik user.

    Prioritas pencocokan:
    1. NIP pegawai = username user
    2. Email pegawai = email user
    3. Email pegawai = username user
    """
    if not user or not user.is_authenticated:
        return None

    qs = Pegawai.objects.select_related('unit_kerja')
    candidates = Q()

    if getattr(user, 'username', None):
        candidates |= Q(nip__iexact=user.username) | Q(email__iexact=user.username)
    if getattr(user, 'email', None):
        candidates |= Q(email__iexact=user.email)

    if not candidates:
        return None
    return qs.filter(candidates).first()


def get_user_profile_unit_kerja(user):
    """Ambil unit kerja dari field Manajemen User bila tersedia."""
    if not user or not user.is_authenticated:
        return None
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'unit_kerja', None)


def get_user_unit_kerja(user):
    """Unit kerja user untuk pembatasan akses.

    Prioritas utama adalah field Unit Kerja/Satker pada menu Manajemen User.
    Jika belum diisi, sistem tetap memakai mekanisme lama: mencocokkan user dengan data pegawai
    berdasarkan NIP/email agar data lama tetap kompatibel.
    """
    profile_unit = get_user_profile_unit_kerja(user)
    if profile_unit:
        return profile_unit
    pegawai = get_user_pegawai(user)
    return getattr(pegawai, 'unit_kerja', None)


def get_user_unit_id(user):
    unit = get_user_unit_kerja(user)
    return unit.pk if unit else None


def require_user_unit_or_all(user):
    if is_biro_umum_user(user):
        return None
    unit_id = get_user_unit_id(user)
    if not unit_id:
        raise PermissionDenied(
            'User belum memiliki Unit Kerja/Satker. '
            'Admin System perlu mengisi field Unit Kerja/Satker pada menu Manajemen User. '
            'Alternatif lama: samakan username user dengan NIP pegawai atau isi email user sama dengan email pegawai.'
        )
    return unit_id


def scope_queryset_by_user(qs, user, scope_type):
    """Batasi queryset sesuai unit kerja user.

    scope_type:
      unit, pegawai, kendaraan, rumah, sip_kendaraan, sip_rumah,
      service_kendaraan, kondisi_kendaraan, perbaikan_rumah
    """
    if is_biro_umum_user(user):
        return qs

    unit_id = require_user_unit_or_all(user)

    if scope_type == 'unit':
        return qs.filter(pk=unit_id)
    if scope_type == 'pegawai':
        return qs.filter(unit_kerja_id=unit_id)
    if scope_type == 'kendaraan':
        return qs.filter(unit_kerja_id=unit_id)
    if scope_type == 'rumah':
        return qs.filter(sip_rumah__pegawai__unit_kerja_id=unit_id).distinct()
    if scope_type == 'sip_kendaraan':
        return qs.filter(Q(kendaraan__unit_kerja_id=unit_id) | Q(pegawai__unit_kerja_id=unit_id)).distinct()
    if scope_type == 'sip_rumah':
        return qs.filter(pegawai__unit_kerja_id=unit_id)
    if scope_type == 'service_kendaraan':
        return qs.filter(kendaraan__unit_kerja_id=unit_id)
    if scope_type == 'kondisi_kendaraan':
        return qs.filter(kendaraan__unit_kerja_id=unit_id)
    if scope_type == 'perbaikan_rumah':
        return qs.filter(
            Q(rumah_dinas__sip_rumah__pegawai__unit_kerja_id=unit_id) |
            Q(pelapor__unit_kerja_id=unit_id)
        ).distinct()

    return qs.none()


class UnitScopedQuerysetMixin:
    scope_type = None

    def get_queryset(self):
        qs = super().get_queryset()
        if self.scope_type:
            qs = scope_queryset_by_user(qs, self.request.user, self.scope_type)
        return qs


class UnitScopedFormMixin:
    """Kirim user ke form agar dropdown FK dibatasi sesuai unit kerja."""
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


def filter_form_fields_by_user(form, user):
    """Batasi dropdown form agar user unit kerja hanya memilih data unitnya."""
    if is_biro_umum_user(user):
        return form

    unit_id = require_user_unit_or_all(user)

    if 'unit_kerja' in form.fields:
        form.fields['unit_kerja'].queryset = UnitKerja.objects.filter(pk=unit_id)
        if not form.instance.pk:
            form.fields['unit_kerja'].initial = unit_id

    if 'pegawai' in form.fields:
        form.fields['pegawai'].queryset = Pegawai.objects.filter(unit_kerja_id=unit_id).order_by('nama')

    if 'pengguna' in form.fields:
        form.fields['pengguna'].queryset = Pegawai.objects.filter(unit_kerja_id=unit_id).order_by('nama')

    if 'pelapor' in form.fields:
        form.fields['pelapor'].queryset = Pegawai.objects.filter(unit_kerja_id=unit_id).order_by('nama')

    if 'kendaraan' in form.fields:
        from master.models import Kendaraan
        form.fields['kendaraan'].queryset = Kendaraan.objects.filter(unit_kerja_id=unit_id).order_by('nomor_polisi')

    if 'rumah_dinas' in form.fields:
        from master.models import RumahDinas
        form.fields['rumah_dinas'].queryset = RumahDinas.objects.filter(
            sip_rumah__pegawai__unit_kerja_id=unit_id
        ).distinct().order_by('kode_rumah')

    return form

class BiroUmumOnlyMixin:
    """Batasi aksi tertentu hanya untuk Biro Umum/superuser."""
    def dispatch(self, request, *args, **kwargs):
        if not is_biro_umum_user(request.user):
            raise PermissionDenied('Aksi ini hanya dapat dilakukan oleh Biro Umum karena datanya lintas satker.')
        return super().dispatch(request, *args, **kwargs)
