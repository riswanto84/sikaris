import random
from datetime import timedelta
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model


JUMLAH_DATA = 500


def get_model(app_label, model_names):
    for name in model_names:
        try:
            return apps.get_model(app_label, name)
        except LookupError:
            continue
    raise LookupError(f"Model tidak ditemukan: {app_label}.{model_names}")


def has_field(model, field_name):
    return any(f.name == field_name for f in model._meta.fields)


def set_if_exists(data, model, field_name, value):
    if not has_field(model, field_name):
        return

    field = model._meta.get_field(field_name)

    if isinstance(value, str):
        max_length = getattr(field, "max_length", None)
        if max_length:
            value = value[:max_length]

    data[field_name] = value


def get_lookup_field(model, preferred_fields):
    for field in preferred_fields:
        if has_field(model, field):
            return field
    return None


def get_attr(obj, field_names, default=None):
    if obj is None:
        return default

    for field in field_names:
        if hasattr(obj, field):
            value = getattr(obj, field)
            if value not in [None, ""]:
                return value

    return default


def get_unit_name(unit):
    return get_attr(unit, ["nama_unit", "nama", "nama_unit_kerja"], str(unit))


def is_pengelola_bmn_user(user):
    role_text = ""

    for field in ["role", "user_role", "level", "jenis_user"]:
        if hasattr(user, field):
            role_text += f" {getattr(user, field)}"

    if hasattr(user, "profile"):
        profile = user.profile
        for field in ["role", "user_role", "level", "jenis_user"]:
            if hasattr(profile, field):
                role_text += f" {getattr(profile, field)}"

    role_text = role_text.upper()
    return "BMN" in role_text or "PENGELOLA" in role_text


def get_user_unit_kerja(user):
    for field in ["unit_kerja", "unit"]:
        if hasattr(user, field):
            unit = getattr(user, field)
            if unit:
                return unit

    if hasattr(user, "profile"):
        profile = user.profile
        for field in ["unit_kerja", "unit"]:
            if hasattr(profile, field):
                unit = getattr(profile, field)
                if unit:
                    return unit

    return None


def get_random_pengelola_bmn_user_by_unit(unit_kerja):
    User = get_user_model()
    users = list(User.objects.all())

    candidates = []

    for user in users:
        if not is_pengelola_bmn_user(user):
            continue

        user_unit = get_user_unit_kerja(user)

        if user_unit and user_unit == unit_kerja:
            candidates.append(user)

    if candidates:
        return random.choice(candidates)

    pengelola_users = [u for u in users if is_pengelola_bmn_user(u)]
    if pengelola_users:
        return random.choice(pengelola_users)

    return User.objects.filter(is_superuser=True).first() or User.objects.first()


def get_pejabat_penerbit_from_unit(unit_kerja):
    """
    Mengambil pejabat penerbit dari konfigurasi Master Unit Kerja.
    Kalau unit direktorat belum punya pejabat penerbit, coba cari unit sekretariat
    pada eselon I yang sama.
    """

    if not unit_kerja:
        return None, "", "", ""

    pejabat = get_attr(unit_kerja, ["pejabat_penerbit_sip_kendaraan"], None)
    jabatan = get_attr(unit_kerja, ["nama_jabatan_penerbit_sip_kendaraan"], "")

    if pejabat:
        nama = get_attr(pejabat, ["nama", "nama_pegawai"], "")
        nip = get_attr(pejabat, ["nip"], "")
        jabatan_final = jabatan or get_attr(pejabat, ["jabatan"], "")
        return pejabat, nama, nip, jabatan_final

    unit_eselon_i = get_attr(unit_kerja, ["unit_eselon_i", "nama_eselon_i"], "")
    nama_unit = get_unit_name(unit_kerja)

    # fallback: cari unit sekretariat dalam eselon I yang sama
    if unit_eselon_i:
        q_units = UnitKerja.objects.all()
        kandidat = []

        for u in q_units:
            u_eselon = get_attr(u, ["unit_eselon_i", "nama_eselon_i"], "")
            u_nama = get_unit_name(u).upper()

            if u_eselon == unit_eselon_i and "SEKRETARIAT" in u_nama:
                kandidat.append(u)

        for u in kandidat:
            pejabat = get_attr(u, ["pejabat_penerbit_sip_kendaraan"], None)
            jabatan = get_attr(u, ["nama_jabatan_penerbit_sip_kendaraan"], "")
            if pejabat:
                nama = get_attr(pejabat, ["nama", "nama_pegawai"], "")
                nip = get_attr(pejabat, ["nip"], "")
                jabatan_final = jabatan or get_attr(pejabat, ["jabatan"], "")
                return pejabat, nama, nip, jabatan_final

    # fallback khusus Biro Umum / Setjen
    if "SEKRETARIAT JENDERAL" in str(unit_eselon_i).upper() or "BIRO UMUM" in nama_unit.upper():
        for u in UnitKerja.objects.all():
            if "BIRO UMUM" in get_unit_name(u).upper():
                pejabat = get_attr(u, ["pejabat_penerbit_sip_kendaraan"], None)
                jabatan = get_attr(u, ["nama_jabatan_penerbit_sip_kendaraan"], "")
                if pejabat:
                    nama = get_attr(pejabat, ["nama", "nama_pegawai"], "")
                    nip = get_attr(pejabat, ["nip"], "")
                    jabatan_final = jabatan or get_attr(pejabat, ["jabatan"], "Kepala Biro Umum")
                    return pejabat, nama, nip, jabatan_final

    return None, "", "", ""


UnitKerja = get_model("master", ["UnitKerja"])
Pegawai = get_model("master", ["Pegawai"])
Kendaraan = get_model("master", ["Kendaraan"])
SIPKendaraan = get_model("kendaraan", ["SIPKendaraan", "SipKendaraan"])


@transaction.atomic
def run():
    kendaraan_list = list(Kendaraan.objects.all())
    pegawai_list = list(Pegawai.objects.all())

    if not kendaraan_list:
        raise Exception("Master kendaraan masih kosong.")

    if not pegawai_list:
        raise Exception("Master pegawai masih kosong.")

    print(f"Jumlah kendaraan tersedia : {len(kendaraan_list)}")
    print(f"Jumlah pegawai tersedia   : {len(pegawai_list)}")

    status_list = [
        "DRAFT",
        "DIAJUKAN",
        "DIAJUKAN",
        "DISETUJUI",
        "MENUNGGU_TTE",
        "TERBIT",
        "DITOLAK",
    ]

    created_count = 0
    updated_count = 0
    tanpa_pejabat_count = 0

    for i in range(1, JUMLAH_DATA + 1):
        kendaraan = random.choice(kendaraan_list)
        unit_kerja = get_attr(kendaraan, ["unit_kerja"], None)

        if unit_kerja:
            pegawai_unit = [
                p for p in pegawai_list
                if get_attr(p, ["unit_kerja"], None) == unit_kerja
            ]
            pegawai = random.choice(pegawai_unit) if pegawai_unit else random.choice(pegawai_list)
        else:
            pegawai = random.choice(pegawai_list)

        created_by = get_random_pengelola_bmn_user_by_unit(unit_kerja)

        pejabat, nama_pejabat, nip_pejabat, jabatan_pejabat = get_pejabat_penerbit_from_unit(unit_kerja)

        if not pejabat:
            tanpa_pejabat_count += 1

        status = random.choice(status_list)

        nomor_sip = f"SIP-KDR-DUMMY-{timezone.now().year}-{i:05d}"

        tanggal_pengajuan = timezone.now() - timedelta(days=random.randint(10, 240))
        tanggal_mulai = tanggal_pengajuan + timedelta(days=random.randint(1, 14))
        tanggal_akhir = tanggal_mulai + timedelta(days=random.randint(180, 365))

        if status == "DRAFT":
            tanggal_diajukan = None
            tanggal_disetujui = None
            tanggal_terbit = None
        elif status == "DIAJUKAN":
            tanggal_diajukan = tanggal_pengajuan + timedelta(days=random.randint(1, 3))
            tanggal_disetujui = None
            tanggal_terbit = None
        elif status == "DITOLAK":
            tanggal_diajukan = tanggal_pengajuan + timedelta(days=random.randint(1, 3))
            tanggal_disetujui = None
            tanggal_terbit = None
        elif status in ["DISETUJUI", "MENUNGGU_TTE"]:
            tanggal_diajukan = tanggal_pengajuan + timedelta(days=random.randint(1, 3))
            tanggal_disetujui = tanggal_diajukan + timedelta(days=random.randint(1, 10))
            tanggal_terbit = None
        else:
            tanggal_diajukan = tanggal_pengajuan + timedelta(days=random.randint(1, 3))
            tanggal_disetujui = tanggal_diajukan + timedelta(days=random.randint(1, 10))
            tanggal_terbit = tanggal_disetujui + timedelta(days=random.randint(1, 7))

        data = {}

        # nomor SIP
        set_if_exists(data, SIPKendaraan, "nomor_sip", nomor_sip)
        set_if_exists(data, SIPKendaraan, "no_sip", nomor_sip)
        set_if_exists(data, SIPKendaraan, "nomor_surat", nomor_sip)

        # relasi utama
        set_if_exists(data, SIPKendaraan, "kendaraan", kendaraan)
        set_if_exists(data, SIPKendaraan, "pegawai", pegawai)
        set_if_exists(data, SIPKendaraan, "pengguna", pegawai)
        set_if_exists(data, SIPKendaraan, "pemegang", pegawai)
        set_if_exists(data, SIPKendaraan, "pemakai", pegawai)
        set_if_exists(data, SIPKendaraan, "unit_kerja", unit_kerja)

        # pembuat/pengaju, jika field tersedia
        if created_by:
            set_if_exists(data, SIPKendaraan, "created_by", created_by)
            set_if_exists(data, SIPKendaraan, "dibuat_oleh", created_by)
            set_if_exists(data, SIPKendaraan, "pengaju", created_by)
            set_if_exists(data, SIPKendaraan, "diajukan_oleh", created_by)

        # tanggal
        set_if_exists(data, SIPKendaraan, "tanggal_pengajuan", tanggal_pengajuan)
        set_if_exists(data, SIPKendaraan, "tanggal_diajukan", tanggal_diajukan)
        set_if_exists(data, SIPKendaraan, "tanggal_mulai", tanggal_mulai)
        set_if_exists(data, SIPKendaraan, "tanggal_awal", tanggal_mulai)
        set_if_exists(data, SIPKendaraan, "tanggal_sip", tanggal_mulai)
        set_if_exists(data, SIPKendaraan, "tanggal_persetujuan", tanggal_disetujui)
        set_if_exists(data, SIPKendaraan, "tanggal_disetujui", tanggal_disetujui)
        set_if_exists(data, SIPKendaraan, "tanggal_terbit", tanggal_terbit)

        # masa berlaku
        set_if_exists(data, SIPKendaraan, "tanggal_akhir", tanggal_akhir)
        set_if_exists(data, SIPKendaraan, "tanggal_berakhir", tanggal_akhir)
        set_if_exists(data, SIPKendaraan, "masa_berlaku_sampai", tanggal_akhir)
        set_if_exists(data, SIPKendaraan, "berlaku_sampai", tanggal_akhir)

        # status
        set_if_exists(data, SIPKendaraan, "status", status)

        if status == "TERBIT":
            set_if_exists(data, SIPKendaraan, "status_tte", "SUDAH_TTE")
        elif status == "MENUNGGU_TTE":
            set_if_exists(data, SIPKendaraan, "status_tte", "MENUNGGU")
        else:
            set_if_exists(data, SIPKendaraan, "status_tte", "BELUM")

        # tujuan/keterangan
        set_if_exists(data, SIPKendaraan, "tujuan_pemakaian", "Menunjang pelaksanaan tugas kedinasan.")
        set_if_exists(data, SIPKendaraan, "keperluan", "Menunjang pelaksanaan tugas kedinasan.")
        set_if_exists(data, SIPKendaraan, "lokasi_penggunaan", "DKI Jakarta")
        set_if_exists(data, SIPKendaraan, "dasar_penerbitan", "Data dummy pengujian alur SIP Kendaraan.")
        set_if_exists(data, SIPKendaraan, "keterangan", "Data dummy Daftar SIP Kendaraan untuk seluruh role Pengelola BMN.")

        # snapshot pengguna
        set_if_exists(data, SIPKendaraan, "nama_pengguna", get_attr(pegawai, ["nama", "nama_pegawai"], ""))
        set_if_exists(data, SIPKendaraan, "nip_pengguna", get_attr(pegawai, ["nip"], ""))
        set_if_exists(data, SIPKendaraan, "jabatan_pengguna", get_attr(pegawai, ["jabatan"], ""))

        # pejabat penerbit
        if pejabat:
            set_if_exists(data, SIPKendaraan, "diajukan_kepada", pejabat)
            set_if_exists(data, SIPKendaraan, "pejabat_penerbit", pejabat)

        set_if_exists(data, SIPKendaraan, "nama_pejabat_penerbit", nama_pejabat)
        set_if_exists(data, SIPKendaraan, "nip_pejabat_penerbit", nip_pejabat)
        set_if_exists(data, SIPKendaraan, "jabatan_pejabat_penerbit", jabatan_pejabat)

        set_if_exists(data, SIPKendaraan, "nama_pejabat_penandatangan", nama_pejabat)
        set_if_exists(data, SIPKendaraan, "nip_pejabat_penandatangan", nip_pejabat)
        set_if_exists(data, SIPKendaraan, "jabatan_pejabat_penandatangan", jabatan_pejabat)

        if status == "DITOLAK":
            set_if_exists(data, SIPKendaraan, "catatan_penolakan", "Data dummy ditolak untuk simulasi revisi.")
        elif status in ["DISETUJUI", "MENUNGGU_TTE", "TERBIT"]:
            set_if_exists(data, SIPKendaraan, "catatan_persetujuan", "Data dummy telah disetujui pejabat penerbit.")

        lookup_field = get_lookup_field(SIPKendaraan, [
            "nomor_sip",
            "no_sip",
            "nomor_surat",
        ])

        if not lookup_field:
            raise Exception("Tidak ditemukan field nomor SIP pada model SIPKendaraan.")

        obj, created = SIPKendaraan.objects.update_or_create(
            **{lookup_field: nomor_sip},
            defaults=data
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    print("")
    print("SELESAI.")
    print(f"Data SIP Kendaraan dibuat baru : {created_count}")
    print(f"Data SIP Kendaraan diupdate    : {updated_count}")
    print(f"Total diproses                 : {JUMLAH_DATA}")
    print(f"Data tanpa pejabat penerbit    : {tanpa_pejabat_count}")
    print("")
    print("Catatan:")
    print("- Jika Data tanpa pejabat penerbit lebih dari 0, lengkapi pejabat penerbit pada Master Unit Kerja.")
    print("- Jalankan fix_snapshot_penerbit_sip_kendaraan jika ingin menyinkronkan ulang snapshot pejabat.")


run()