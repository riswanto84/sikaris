from django.core.exceptions import PermissionDenied
from django.db.models import Q
from core.roles import is_sekretaris_jenderal, is_kepala_biro_umum, is_pengelola_bmn, is_admin_system, can_approve_sip_kendaraan

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




def is_global_bmn_scope_user(user):
    """User yang boleh melihat/mengelola data lintas seluruh Kementerian.

    Perbaikan 2026-06-15:
    - Admin System tetap global.
    - Pengelola BMN, termasuk yang berada di Biro Umum/Setjen, TIDAK global.
      Pengelola BMN dibatasi pada unit Eselon I-nya.
    - User Biro Umum non-BMN tetap dipertahankan global untuk kompatibilitas fitur
      administrasi lama.
    """
    if is_admin_system(user):
        return True
    if is_pengelola_bmn(user):
        return False
    return is_biro_umum_user(user)

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




# ==========================================================
# UNIT SCOPE BMN SEKRETARIAT KANTOR PUSAT
# ==========================================================
# Ketentuan akses:
# 1. Admin System/Biro Umum tetap lintas seluruh satker.
# 2. Role Pengelola BMN pada Sekretariat kantor pusat Eselon I
#    dapat melihat/mengelola master data Pegawai, Kendaraan, Rumah Negara,
#    SIP, service, dan dashboard untuk unit di bawah Eselon I-nya.
# 3. Role Pengelola BMN pada Sentra/Balai hanya melihat data unitnya sendiri.
#
# Agar kompatibel dengan database lama, scope ini bekerja dengan 3 cara:
# - Jika nanti model UnitKerja punya field kode_eselon_1/unit_induk, field itu dipakai.
# - Jika belum ada field tersebut, sistem memakai pola nama unit kerja.
# - Sentra/Balai selalu dipaksa scope unit sendiri.

SEKRETARIAT_PREFIXES = (
    'SEKRETARIAT DIREKTORAT JENDERAL ',
    'SEKRETARIAT INSPEKTORAT JENDERAL',
    'SEKRETARIAT BADAN ',
    'SEKRETARIAT UTAMA ',
)

SENTRA_BALAI_KEYWORDS = ('SENTRA', 'BALAI')


def _model_has_field(model, field_name):
    return any(getattr(f, 'name', None) == field_name for f in model._meta.fields)


def _is_sentra_or_balai_unit(unit):
    if not unit:
        return False
    jenis = _norm(getattr(unit, 'jenis_unit', ''))
    nama = _norm(getattr(unit, 'nama_unit', ''))
    return jenis in ('SENTRA', 'BALAI') or nama.startswith('SENTRA ') or nama.startswith('BALAI ')


def _is_sekretariat_kantor_pusat_unit(unit):
    if not unit:
        return False
    # Sentra/Balai tidak pernah menjadi scope induk.
    if _is_sentra_or_balai_unit(unit):
        return False
    nama = _norm(getattr(unit, 'nama_unit', ''))
    return any(nama.startswith(prefix) or nama == prefix.strip() for prefix in SEKRETARIAT_PREFIXES)


def _derive_eselon_keyword_from_sekretariat(unit):
    """Ambil kata kunci Eselon I dari nama sekretariat.

    Contoh:
    Sekretariat Direktorat Jenderal Rehabilitasi Sosial
    -> REHABILITASI SOSIAL
    """
    nama = _norm(getattr(unit, 'nama_unit', ''))
    replacements = [
        'SEKRETARIAT DIREKTORAT JENDERAL ',
        'SEKRETARIAT INSPEKTORAT JENDERAL ',
        'SEKRETARIAT BADAN ',
        'SEKRETARIAT UTAMA ',
    ]
    for prefix in replacements:
        if nama.startswith(prefix):
            return nama.replace(prefix, '', 1).strip()
    if nama == 'SEKRETARIAT INSPEKTORAT JENDERAL':
        return 'INSPEKTORAT JENDERAL'
    return nama.replace('SEKRETARIAT ', '', 1).strip()


def _unit_matches_eselon_keyword(unit, keyword):
    nama = _norm(getattr(unit, 'nama_unit', ''))
    jenis = _norm(getattr(unit, 'jenis_unit', ''))
    if not nama or not keyword:
        return False
    if _is_sentra_or_balai_unit(unit):
        return False
    # Direktorat di bawah Ditjen biasanya mengandung kata kunci bidang Eselon I,
    # misal: Direktorat Rehabilitasi Sosial Anak, Direktorat Rehabilitasi Sosial Lanjut Usia.
    if keyword in nama:
        return True
    # Fallback untuk beberapa nama yang tidak lengkap: cocokkan token penting.
    tokens = [t for t in keyword.split() if len(t) >= 5]
    if tokens and nama.startswith(('DIREKTORAT ', 'PUSAT ', 'SEKRETARIAT ')):
        return all(t in nama for t in tokens[:2])
    return False



# ==========================================================
# DETEKSI UNIT ESELON I UNTUK SCOPE PENGELOLA BMN
# ==========================================================
# Karena model UnitKerja saat ini belum memiliki parent/kode_eselon_i,
# scope Eselon I diturunkan dari nama unit. Aturan ini dibuat eksplisit agar
# Pengelola BMN Biro Umum tidak lagi melihat semua kementerian, tetapi hanya
# unit di bawah Sekretariat Jenderal; demikian juga BMN pada Ditjen/Itjen lain.

SETJEN_UNIT_KEYWORDS = (
    'SEKRETARIAT JENDERAL', 'SETJEN', 'BIRO ', 'BIRO UMUM',
    'PUSAT DATA', 'PUSDATIN', 'PUSAT PENDIDIKAN', 'PUSDIKLAT',
)

ESELON_I_SCOPE_RULES = {
    'SETJEN': (
        'SEKRETARIAT JENDERAL', 'SETJEN', 'BIRO ', 'BIRO UMUM', 'BIRO HUKUM',
        'BIRO ORGANISASI', 'BIRO KEUANGAN', 'BIRO PERENCANAAN', 'PUSAT DATA',
        'PUSDATIN',
    ),
    'REHSOS': (
        'REHABILITASI SOSIAL',
    ),
    'DAYASOS': (
        'PEMBERDAYAAN SOSIAL', 'KOMUNITAS ADAT', 'KEWIRAUSAHAAN SOSIAL',
        'KELOMPOK RENTAN', 'PEMBERDAYAAN MASYARAKAT', 'KEPAHLAWANAN',
        'KEPERINTISAN', 'KESETIAKAWANAN', 'RESTORASI SOSIAL',
        'POTENSI DAN SUMBER DAYA SOSIAL',
    ),
    'LINJAMSOS': (
        'PERLINDUNGAN DAN JAMINAN SOSIAL', 'JAMINAN SOSIAL',
        'PERLINDUNGAN SOSIAL', 'BENCANA ALAM', 'BENCANA SOSIAL',
        'KORBAN TINDAK KEKERASAN', 'PEKERJA MIGRAN',
        'SUMBER DANA BANTUAN SOSIAL', 'BANTUAN SOSIAL',
    ),
    'ITJEN': (
        'INSPEKTORAT JENDERAL', 'INSPEKTORAT BIDANG', 'INSPEKTORAT ',
        'INVESTIGASI', 'PENUNJANG',
    ),
    'BADIKLIT': (
        'BADAN PENDIDIKAN', 'PELATIHAN', 'PENYULUHAN SOSIAL',
        'PENDIDIKAN, PELATIHAN', 'DIKLAT',
    ),
}


def _unit_scope_text(unit):
    if not unit:
        return ''
    values = [
        getattr(unit, 'nama_unit', ''),
        getattr(unit, 'jenis_unit', ''),
        getattr(unit, 'keterangan', ''),
    ]
    # Jika pada versi berikutnya field eselon_i ditambahkan, otomatis ikut terbaca.
    for field in ('unit_eselon_i', 'nama_eselon_i', 'eselon_i', 'kode_eselon_1'):
        if hasattr(unit, field):
            values.append(getattr(unit, field) or '')
    return _norm(' '.join(str(v) for v in values if v))


def _derive_eselon_scope_key(unit):
    text = _unit_scope_text(unit)
    if not text:
        return None
    if _is_sentra_or_balai_unit(unit):
        return None

    # Biro Umum dan unit Setjen harus masuk scope Sekretariat Jenderal.
    if any(k in text for k in ESELON_I_SCOPE_RULES['SETJEN']):
        return 'SETJEN'

    # Urutan dibuat dari yang paling spesifik.
    for key in ('REHSOS', 'DAYASOS', 'LINJAMSOS', 'ITJEN', 'BADIKLIT'):
        if any(k in text for k in ESELON_I_SCOPE_RULES[key]):
            return key

    # Kompatibilitas pola sekretariat lama.
    if _is_sekretariat_kantor_pusat_unit(unit):
        keyword = _derive_eselon_keyword_from_sekretariat(unit)
        if 'REHABILITASI SOSIAL' in keyword:
            return 'REHSOS'
        if 'PEMBERDAYAAN SOSIAL' in keyword:
            return 'DAYASOS'
        if 'PERLINDUNGAN' in keyword or 'JAMINAN SOSIAL' in keyword:
            return 'LINJAMSOS'
        if 'INSPEKTORAT' in keyword:
            return 'ITJEN'
    return None


def _unit_matches_eselon_scope_key(unit, scope_key):
    if not unit or not scope_key:
        return False
    if _is_sentra_or_balai_unit(unit):
        return False
    text = _unit_scope_text(unit)
    return any(k in text for k in ESELON_I_SCOPE_RULES.get(scope_key, ()))


def _get_eselon_scope_unit_ids(unit):
    scope_key = _derive_eselon_scope_key(unit)
    if not scope_key:
        return {unit.pk} if unit else set()
    ids = set()
    for candidate in UnitKerja.objects.all().only('id', 'nama_unit', 'jenis_unit', 'keterangan'):
        if candidate.pk == unit.pk or _unit_matches_eselon_scope_key(candidate, scope_key):
            ids.add(candidate.pk)
    return ids

def get_accessible_unit_ids_for_user(user):
    """Return daftar unit_id yang boleh diakses user non-global.

    Return None berarti user global/lintas semua unit.
    """
    if is_global_bmn_scope_user(user):
        return None

    unit = get_user_unit_kerja(user)
    if not unit:
        return []

    # BMN Sentra/Balai: hanya unitnya sendiri.
    if _is_sentra_or_balai_unit(unit):
        return [unit.pk]

    # Pengelola BMN pada unit kantor pusat dibatasi pada Eselon I-nya.
    # Contoh: BMN Biro Umum hanya Sekretariat Jenderal; BMN Ditjen Rehsos
    # hanya Sekretariat/Direktorat di bawah Ditjen Rehsos.
    if is_pengelola_bmn(user):
        ids = _get_eselon_scope_unit_ids(unit)
        return sorted(ids) if ids else [unit.pk]

    # Pejabat penerbit yang juga membutuhkan scope umum mengikuti Eselon I-nya,
    # kecuali Sentra/Balai yang sudah dipaksa di atas.
    if can_approve_sip_kendaraan(user):
        ids = _get_eselon_scope_unit_ids(unit)
        return sorted(ids) if ids else [unit.pk]

    # Role lain default unit sendiri.
    return [unit.pk]


def get_accessible_units_queryset_for_user(user):
    unit_ids = get_accessible_unit_ids_for_user(user)
    if unit_ids is None:
        return UnitKerja.objects.all()
    return UnitKerja.objects.filter(pk__in=unit_ids)


def get_dashboard_scope_label(user):
    if is_global_bmn_scope_user(user):
        return 'Semua Satker / Unit Kerja'
    unit = get_user_unit_kerja(user)
    if not unit:
        return 'Unit kerja belum diatur'
    if _is_sentra_or_balai_unit(unit):
        return unit.nama_unit
    scope_key = _derive_eselon_scope_key(unit)
    if is_pengelola_bmn(user) and scope_key:
        label_map = {
            'SETJEN': 'Sekretariat Jenderal',
            'REHSOS': 'Direktorat Jenderal Rehabilitasi Sosial',
            'DAYASOS': 'Direktorat Jenderal Pemberdayaan Sosial',
            'LINJAMSOS': 'Direktorat Jenderal Perlindungan dan Jaminan Sosial',
            'ITJEN': 'Inspektorat Jenderal',
            'BADIKLIT': 'Badan Pendidikan, Pelatihan, dan Penyuluhan Sosial',
        }
        return f'{unit.nama_unit} - cakupan {label_map.get(scope_key, "Eselon I")}'
    return unit.nama_unit


def _raise_missing_unit_permission():
    raise PermissionDenied(
        'User belum memiliki Unit Kerja/Satker. '
        'Admin System perlu mengisi field Unit Kerja/Satker pada menu Manajemen User. '
        'Alternatif lama: samakan username user dengan NIP pegawai atau isi email user sama dengan email pegawai.'
    )


def require_user_unit_or_all(user):
    """Kompatibilitas lama: return satu unit_id milik user.

    Beberapa fitur transaksi lama memakai field unit_kerja_id tunggal.
    Untuk scope master/dashboard baru gunakan require_user_unit_ids_or_all().
    """
    if is_global_bmn_scope_user(user):
        return None
    unit_id = get_user_unit_id(user)
    if not unit_id:
        _raise_missing_unit_permission()
    return unit_id


def require_user_unit_ids_or_all(user):
    if is_global_bmn_scope_user(user):
        return None
    unit_ids = get_accessible_unit_ids_for_user(user)
    if not unit_ids:
        _raise_missing_unit_permission()
    return unit_ids


def scope_queryset_by_user(qs, user, scope_type):
    """Batasi queryset sesuai unit kerja user.

    scope_type:
      unit, pegawai, kendaraan, rumah, sip_kendaraan, sip_rumah,
      service_kendaraan, kondisi_kendaraan, perbaikan_rumah, psp
    """
    # Khusus pejabat penerbit SIP Kendaraan, pembatasan harus dieksekusi
    # sebelum global Biro Umum. Kepala Biro Umum memang berada di Biro Umum,
    # tetapi untuk daftar/detail persetujuan SIP Kendaraan kewenangannya hanya
    # unit kerja di bawah Sekretariat Jenderal.
    if can_approve_sip_kendaraan(user) and scope_type == 'sip_kendaraan' and not is_admin_system(user):
        from kendaraan.sip_penerbit import get_sip_kendaraan_approval_unit_ids_for_user
        unit_ids = get_sip_kendaraan_approval_unit_ids_for_user(user)
        if unit_ids is None:
            return qs
        if not unit_ids:
            return qs.none()
        return qs.filter(Q(kendaraan__unit_kerja_id__in=unit_ids) | Q(pegawai__unit_kerja_id__in=unit_ids)).distinct()

    # Admin System dan Biro Umum boleh lintas unit kerja untuk fitur umum.
    # Pengelola BMN TIDAK boleh lintas unit; tetap dibatasi sesuai unit kerja user.
    if is_global_bmn_scope_user(user):
        return qs

    # Sekjen khusus SIP Rumah Negara.
    if is_sekretaris_jenderal(user) and scope_type == 'sip_rumah':
        return qs

    unit_ids = require_user_unit_ids_or_all(user)

    if scope_type == 'unit':
        return qs.filter(pk__in=unit_ids)
    if scope_type == 'pegawai':
        return qs.filter(unit_kerja_id__in=unit_ids)
    if scope_type == 'kendaraan':
        return qs.filter(unit_kerja_id__in=unit_ids)
    if scope_type == 'rumah':
        return qs.filter(unit_kerja_id__in=unit_ids)
    if scope_type == 'sip_kendaraan':
        return qs.filter(Q(kendaraan__unit_kerja_id__in=unit_ids) | Q(pegawai__unit_kerja_id__in=unit_ids)).distinct()
    if scope_type == 'sip_rumah':
        return qs.filter(Q(rumah_dinas__unit_kerja_id__in=unit_ids) | Q(pegawai__unit_kerja_id__in=unit_ids) | Q(penghuni__unit_kerja_id__in=unit_ids)).distinct()
    if scope_type == 'service_kendaraan':
        return qs.filter(kendaraan__unit_kerja_id__in=unit_ids)
    if scope_type == 'kondisi_kendaraan':
        return qs.filter(kendaraan__unit_kerja_id__in=unit_ids)
    if scope_type == 'perbaikan_rumah':
        return qs.filter(
            Q(rumah_dinas__unit_kerja_id__in=unit_ids) |
            Q(pelapor__unit_kerja_id__in=unit_ids)
        ).distinct()
    if scope_type == 'psp':
        return qs.filter(
            Q(unit_kerja_id__in=unit_ids) |
            Q(pemohon__unit_kerja_id__in=unit_ids)
        ).distinct()
    if scope_type == 'penghapusan_bmn':
        return qs.filter(
            Q(unit_kerja_id__in=unit_ids) |
            Q(pemohon__unit_kerja_id__in=unit_ids) |
            Q(kendaraan__unit_kerja_id__in=unit_ids) |
            Q(rumah_negara__unit_kerja_id__in=unit_ids) |
            Q(tanah_negara__unit_kerja_id__in=unit_ids)
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
    # Admin System dan Biro Umum boleh memilih data lintas unit kerja.
    # Pengelola BMN harus tetap dibatasi sesuai Unit Kerja/Satker miliknya.
    if is_global_bmn_scope_user(user):
        return form

    # Form SIP yang diedit Sekretaris Jenderal harus tetap bisa menampilkan
    # pilihan kendaraan/rumah/pegawai lintas satker.
    if is_sekretaris_jenderal(user):
        model_name = getattr(getattr(form, 'Meta', None), 'model', None)
        model_name = getattr(model_name, '__name__', '')
        if model_name in ['SIPKendaraan', 'SIPRumahDinas']:
            return form

    unit_ids = require_user_unit_ids_or_all(user)
    own_unit = get_user_unit_kerja(user)

    if 'unit_kerja' in form.fields:
        form.fields['unit_kerja'].queryset = UnitKerja.objects.filter(pk__in=unit_ids).order_by('nama_unit')
        if not form.instance.pk and own_unit:
            form.fields['unit_kerja'].initial = own_unit.pk

    if 'pegawai' in form.fields:
        form.fields['pegawai'].queryset = Pegawai.objects.filter(unit_kerja_id__in=unit_ids).order_by('nama')

    if 'pengguna' in form.fields:
        form.fields['pengguna'].queryset = Pegawai.objects.filter(unit_kerja_id__in=unit_ids).order_by('nama')

    if 'pelapor' in form.fields:
        form.fields['pelapor'].queryset = Pegawai.objects.filter(unit_kerja_id__in=unit_ids).order_by('nama')

    if 'penghuni' in form.fields:
        form.fields['penghuni'].queryset = Pegawai.objects.filter(unit_kerja_id__in=unit_ids).order_by('nama')

    if 'kendaraan' in form.fields:
        from master.models import Kendaraan
        form.fields['kendaraan'].queryset = Kendaraan.objects.filter(unit_kerja_id__in=unit_ids).order_by('nomor_polisi')

    if 'rumah_dinas' in form.fields:
        from master.models import RumahDinas
        form.fields['rumah_dinas'].queryset = RumahDinas.objects.filter(unit_kerja_id__in=unit_ids).order_by('kode_rumah')

    return form

class BiroUmumOnlyMixin:
    """Batasi aksi tertentu hanya untuk Biro Umum/superuser."""
    def dispatch(self, request, *args, **kwargs):
        if not is_biro_umum_user(request.user):
            raise PermissionDenied('Aksi ini hanya dapat dilakukan oleh Biro Umum karena datanya lintas satker.')
        return super().dispatch(request, *args, **kwargs)
