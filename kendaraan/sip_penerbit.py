from master.models import Pegawai, UnitKerja


SETJEN_KEYWORDS = [
    'SEKRETARIAT JENDERAL',
    'SETJEN',
    'BIRO UMUM',
]

# Mapping ini dipakai sebagai fallback bila tabel UnitKerja belum punya relasi induk/eselon I.
ESELON_I_SECRETARIAT_MAP = [
    ('REHABILITASI SOSIAL', 'Sekretariat Direktorat Jenderal Rehabilitasi Sosial'),
    ('PEMBERDAYAAN SOSIAL', 'Sekretariat Direktorat Jenderal Pemberdayaan Sosial'),
    ('PERLINDUNGAN DAN JAMINAN SOSIAL', 'Sekretariat Direktorat Jenderal Perlindungan dan Jaminan Sosial'),
    ('LINJAMSOS', 'Sekretariat Direktorat Jenderal Perlindungan dan Jaminan Sosial'),
    ('INSPEKTORAT JENDERAL', 'Sekretariat Inspektorat Jenderal'),
    ('ITJEN', 'Sekretariat Inspektorat Jenderal'),
]


def _norm(value):
    return (value or '').strip().upper()


def _unit_name(unit):
    return getattr(unit, 'nama_unit', '') or str(unit or '')


def _unit_eselon_i(unit):
    return (getattr(unit, 'unit_eselon_i', None) or getattr(unit, 'nama_eselon_i', None) or '')


def get_unit_for_sip_kendaraan(sip):
    """Ambil unit sumber SIP Kendaraan.

    SIP Kendaraan melekat pada kendaraan; pegawai/unit_kerja hanya fallback untuk
    data lama yang belum lengkap.
    """
    if getattr(sip, 'kendaraan_id', None) and getattr(sip.kendaraan, 'unit_kerja_id', None):
        return sip.kendaraan.unit_kerja
    if getattr(sip, 'unit_kerja_id', None):
        return sip.unit_kerja
    if getattr(sip, 'pegawai_id', None) and getattr(sip.pegawai, 'unit_kerja_id', None):
        return sip.pegawai.unit_kerja
    return None


def _find_unit_by_name_exact_or_contains(name):
    if not name:
        return None
    unit = UnitKerja.objects.filter(nama_unit__iexact=name).first()
    if unit:
        return unit
    return UnitKerja.objects.filter(nama_unit__icontains=name).order_by('nama_unit').first()


def _find_biro_umum_unit():
    """Cari Unit Kerja Biro Umum; prioritaskan yang sudah punya pejabat penerbit."""
    return (
        UnitKerja.objects.filter(nama_unit__icontains='Biro Umum', pejabat_penerbit_sip_kendaraan__isnull=False).order_by('nama_unit').first()
        or UnitKerja.objects.filter(jenis_unit='BIRO_UMUM', pejabat_penerbit_sip_kendaraan__isnull=False).order_by('nama_unit').first()
        or UnitKerja.objects.filter(nama_unit__icontains='Biro Umum').order_by('nama_unit').first()
        or UnitKerja.objects.filter(jenis_unit='BIRO_UMUM').order_by('nama_unit').first()
    )


def _find_secretariat_unit_by_eselon(eselon_text):
    eselon_upper = _norm(eselon_text)
    if not eselon_upper:
        return None
    for keyword, sekretariat_name in ESELON_I_SECRETARIAT_MAP:
        if keyword in eselon_upper:
            return _find_unit_by_name_exact_or_contains(sekretariat_name)
    qs = UnitKerja.objects.filter(nama_unit__icontains='Sekretariat')
    for token in eselon_upper.split():
        if len(token) > 4 and token not in {'DIREKTORAT', 'JENDERAL', 'INSPEKTORAT', 'BIDANG'}:
            candidate = qs.filter(nama_unit__icontains=token).order_by('nama_unit').first()
            if candidate:
                return candidate
    return None


def _is_sentra(unit):
    nama = _norm(_unit_name(unit))
    jenis = _norm(getattr(unit, 'jenis_unit', ''))
    return jenis == 'SENTRA' or nama.startswith('SENTRA ') or ' SENTRA ' in f' {nama} '


def _is_balai(unit):
    nama = _norm(_unit_name(unit))
    jenis = _norm(getattr(unit, 'jenis_unit', ''))
    return jenis == 'BALAI' or nama.startswith('BALAI ') or ' BALAI ' in f' {nama} '


def _is_setjen_related_unit(unit):
    if not unit:
        return False
    nama = _norm(_unit_name(unit))
    jenis = _norm(getattr(unit, 'jenis_unit', ''))
    eselon = _norm(_unit_eselon_i(unit))

    if _is_sentra(unit) or _is_balai(unit):
        return False
    if jenis in ('DITJEN', 'ITJEN', 'BADAN') and 'BIRO UMUM' not in nama:
        return False
    if any(k in eselon for k in SETJEN_KEYWORDS):
        return True
    if any(k in nama for k in SETJEN_KEYWORDS):
        return True
    if nama.startswith('BIRO ') or ' BIRO ' in f' {nama} ':
        return True
    # Pusat di lingkungan Setjen/Kantor Pusat tetap tidak boleh menarik Ditjen/Sentra/Balai.
    if nama.startswith('PUSAT ') and not any(x in nama for x in ['DIREKTORAT JENDERAL', 'INSPEKTORAT', 'SENTRA', 'BALAI']):
        return True
    return False


def _is_secretariat_eselon_i(unit):
    nama = _norm(_unit_name(unit))
    return nama.startswith('SEKRETARIAT DIREKTORAT JENDERAL') or nama.startswith('SEKRETARIAT INSPEKTORAT JENDERAL') or nama.startswith('SEKRETARIAT BADAN')


def get_target_unit_penerbit_sip_kendaraan(unit):
    """Menentukan unit pejabat tujuan pengajuan SIP Kendaraan.

    Aturan proses bisnis terakhir:
    1. Unit di bawah Sekretariat Jenderal -> Biro Umum/Kepala Biro Umum.
    2. Unit Eselon I selain Setjen -> Sekretariat UKE I/UKE II masing-masing.
    3. Sentra -> Kepala Sentra pada unit Sentra itu sendiri.
    4. Balai -> Kepala Balai pada unit Balai itu sendiri.
    """
    if not unit:
        return None

    nama = _norm(_unit_name(unit))
    eselon = _norm(_unit_eselon_i(unit))

    if _is_sentra(unit) or _is_balai(unit):
        return unit

    if _is_setjen_related_unit(unit):
        return _find_biro_umum_unit() or unit

    if _is_secretariat_eselon_i(unit):
        return unit

    # Jika ada field unit_eselon_i/nama_eselon_i, arahkan ke Sekretariat UKE tersebut.
    target_from_eselon = _find_secretariat_unit_by_eselon(eselon)
    if target_from_eselon:
        return target_from_eselon

    # Fallback dari pola nama Direktorat/Inspektorat.
    for keyword, sekretariat_name in ESELON_I_SECRETARIAT_MAP:
        if keyword in nama:
            return _find_unit_by_name_exact_or_contains(sekretariat_name) or unit

    return unit


def _find_pegawai_by_keywords(unit, keywords):
    qs = Pegawai.objects.select_related('unit_kerja').all()
    unit_qs = qs.filter(unit_kerja=unit) if unit else qs

    for keyword in keywords:
        keyword = (keyword or '').strip()
        if not keyword:
            continue
        pegawai = (
            unit_qs.filter(jabatan__icontains=keyword, status_pegawai__iexact='Aktif').order_by('nama').first()
            or unit_qs.filter(jabatan__icontains=keyword).order_by('nama').first()
            or qs.filter(jabatan__icontains=keyword, status_pegawai__iexact='Aktif').order_by('nama').first()
            or qs.filter(jabatan__icontains=keyword).order_by('nama').first()
        )
        if pegawai:
            return pegawai
    return None


def suggest_jabatan_penerbit(unit):
    if not unit:
        return 'Pejabat Penerbit SIP Kendaraan'

    target_unit = get_target_unit_penerbit_sip_kendaraan(unit) or unit
    configured = getattr(target_unit, 'nama_jabatan_penerbit_sip_kendaraan', None)
    if configured:
        return configured

    # Fallback konfigurasi lama yang tersimpan di unit sumber.
    source_configured = getattr(unit, 'nama_jabatan_penerbit_sip_kendaraan', None)
    if source_configured:
        return source_configured

    nama = _unit_name(target_unit)
    upper = _norm(nama)
    jenis = _norm(getattr(target_unit, 'jenis_unit', ''))

    if jenis == 'BIRO_UMUM' or 'BIRO UMUM' in upper:
        return 'Kepala Biro Umum'
    if _is_sentra(target_unit):
        return f'Kepala {nama}'
    if _is_balai(target_unit):
        return f'Kepala {nama}'
    if 'INSPEKTORAT JENDERAL' in upper:
        return 'Sekretaris Inspektorat Jenderal'
    if 'DIREKTORAT JENDERAL' in upper:
        return f'Sekretaris {nama.replace("Sekretariat ", "")}'
    if jenis in ['DITJEN', 'ITJEN', 'BADAN']:
        return f'Sekretaris {nama.replace("Sekretariat ", "")}'
    if jenis == 'PUSAT' or upper.startswith('PUSAT '):
        return f'Kepala {nama}'
    return 'Pejabat Penerbit SIP Kendaraan'


def get_pejabat_penerbit_sip_kendaraan(sip):
    unit = get_unit_for_sip_kendaraan(sip)
    target_unit = get_target_unit_penerbit_sip_kendaraan(unit)

    if target_unit and getattr(target_unit, 'pejabat_penerbit_sip_kendaraan_id', None):
        return target_unit.pejabat_penerbit_sip_kendaraan

    # Fallback khusus Setjen: selalu coba Biro Umum.
    if _is_setjen_related_unit(unit):
        biro = _find_biro_umum_unit()
        if biro and getattr(biro, 'pejabat_penerbit_sip_kendaraan_id', None):
            return biro.pejabat_penerbit_sip_kendaraan

    # Fallback data lama: pejabat mungkin tersimpan pada unit sumber.
    if unit and getattr(unit, 'pejabat_penerbit_sip_kendaraan_id', None):
        return unit.pejabat_penerbit_sip_kendaraan

    jabatan = suggest_jabatan_penerbit(unit)
    keywords = [jabatan]
    if target_unit:
        target_name = _norm(_unit_name(target_unit))
        if 'BIRO UMUM' in target_name:
            keywords += ['Kepala Biro Umum']
        elif _is_sentra(target_unit):
            keywords += ['Kepala Sentra', 'Kepala']
        elif _is_balai(target_unit):
            keywords += ['Kepala Balai', 'Kepala']
        else:
            keywords += ['Sekretaris']
    return _find_pegawai_by_keywords(target_unit, keywords)


def apply_snapshot_penerbit_sip_kendaraan(sip, force=False):
    unit = get_unit_for_sip_kendaraan(sip)
    pegawai = get_pejabat_penerbit_sip_kendaraan(sip)
    jabatan = suggest_jabatan_penerbit(unit)

    if pegawai and not jabatan:
        jabatan = pegawai.jabatan

    if force or not getattr(sip, 'pejabat_penerbit_sip_kendaraan_id', None):
        sip.pejabat_penerbit_sip_kendaraan = pegawai
    if force or not getattr(sip, 'nama_pejabat_penerbit_sip_kendaraan', None):
        sip.nama_pejabat_penerbit_sip_kendaraan = getattr(pegawai, 'nama', '') or ''
    if force or not getattr(sip, 'nip_pejabat_penerbit_sip_kendaraan', None):
        sip.nip_pejabat_penerbit_sip_kendaraan = getattr(pegawai, 'nip', '') or ''
    if force or not getattr(sip, 'jabatan_pejabat_penerbit_sip_kendaraan', None):
        sip.jabatan_pejabat_penerbit_sip_kendaraan = jabatan
    if force or not getattr(sip, 'pejabat_penandatangan', None):
        # Field lama tetap diisi untuk kompatibilitas tampilan, tetapi sumber benar
        # adalah snapshot pejabat_penerbit_sip_kendaraan di atas.
        sip.pejabat_penandatangan = jabatan or 'Pejabat Penerbit SIP Kendaraan'
    return sip


def get_label_tujuan_pengajuan_sip_kendaraan(sip):
    unit = get_unit_for_sip_kendaraan(sip)
    return suggest_jabatan_penerbit(unit)


def user_is_penerbit_for_sip(user, sip):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    role_names = set(user.groups.values_list('name', flat=True))
    if 'Admin System' in role_names:
        return True

    unit = get_unit_for_sip_kendaraan(sip)
    target_unit = get_target_unit_penerbit_sip_kendaraan(unit)
    profile_unit = getattr(getattr(user, 'profile', None), 'unit_kerja', None)
    if not profile_unit:
        try:
            from core.access import get_user_unit_kerja
            profile_unit = get_user_unit_kerja(user)
        except Exception:
            profile_unit = None

    same_target_unit = bool(target_unit and profile_unit and profile_unit.pk == target_unit.pk)
    target_name = _norm(_unit_name(target_unit))
    target_jenis = _norm(getattr(target_unit, 'jenis_unit', ''))

    if 'Kepala Biro Umum' in role_names and (target_jenis == 'BIRO_UMUM' or 'BIRO UMUM' in target_name):
        return True

    penerbit_roles = {'Pejabat Penerbit SIP', 'Sekretaris Ditjen', 'Sekretaris Eselon I', 'Sekretaris UKE II', 'Kepala Sentra', 'Kepala Balai'}
    if role_names.intersection(penerbit_roles) and same_target_unit:
        return True

    pegawai = get_pejabat_penerbit_sip_kendaraan(sip)
    if pegawai:
        username = str(getattr(user, 'username', '') or '').lower()
        email = str(getattr(user, 'email', '') or '').lower()
        if username and username in [str(getattr(pegawai, 'nip', '') or '').lower(), str(getattr(pegawai, 'email', '') or '').lower()]:
            return True
        if email and email == str(getattr(pegawai, 'email', '') or '').lower():
            return True

    return False


def get_setjen_unit_ids_for_kabiro_umum():
    ids = []
    for unit in UnitKerja.objects.all().only('id', 'nama_unit', 'jenis_unit'):
        if _is_setjen_related_unit(unit):
            ids.append(unit.pk)
    return ids


def get_sip_kendaraan_approval_unit_ids_for_user(user):
    """Scope daftar persetujuan SIP Kendaraan untuk pejabat penerbit."""
    if not user or not user.is_authenticated:
        return []
    role_names = set(user.groups.values_list('name', flat=True))
    if user.is_superuser or 'Admin System' in role_names:
        return None

    if 'Kepala Biro Umum' in role_names:
        return get_setjen_unit_ids_for_kabiro_umum()

    try:
        from core.access import get_accessible_unit_ids_for_user, get_user_unit_kerja
        profile_unit = get_user_unit_kerja(user)
    except Exception:
        profile_unit = getattr(getattr(user, 'profile', None), 'unit_kerja', None)

    if not profile_unit:
        return []

    if _is_sentra(profile_unit) or _is_balai(profile_unit):
        return [profile_unit.pk]

    try:
        ids = get_accessible_unit_ids_for_user(user)
        if ids is None:
            return [profile_unit.pk]
        return ids
    except Exception:
        return [profile_unit.pk]
