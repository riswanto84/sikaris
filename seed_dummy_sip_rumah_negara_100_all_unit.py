import random
from datetime import timedelta
from django.apps import apps
from django.db import transaction
from django.utils import timezone


JUMLAH_DATA = 100


def get_model(app_label, model_names, required=True):
    for name in model_names:
        try:
            return apps.get_model(app_label, name)
        except LookupError:
            continue

    if required:
        raise LookupError(f"Model tidak ditemukan: {app_label}.{model_names}")

    return None


def has_field(model, field_name):
    if not model:
        return False
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


def get_lookup_field(model, fields):
    for field in fields:
        if has_field(model, field):
            return field
    return None


def get_attr(obj, fields, default=None):
    if obj is None:
        return default

    for field in fields:
        if hasattr(obj, field):
            value = getattr(obj, field)
            if value not in [None, ""]:
                return value

    return default


def get_unit_name(unit):
    return get_attr(unit, ["nama_unit", "nama", "nama_unit_kerja"], str(unit))


UnitKerja = get_model("master", ["UnitKerja"])
Pegawai = get_model("master", ["Pegawai"])
Rumah = get_model("master", ["RumahNegara", "RumahDinas"])

SIPRumah = get_model("rumah_dinas", [
    "SIPRumahNegara",
    "SipRumahNegara",
    "SIPRumahDinas",
    "SipRumahDinas",
])


def get_pejabat_penerbit_rumah(unit_kerja):
    """
    Untuk SIP Rumah Negara, default pejabat penandatangan biasanya Sekjen.
    Jika model/unit punya field pejabat khusus, script akan mencoba mengambilnya.
    Kalau tidak ada, akan diisi snapshot teks Sekretaris Jenderal.
    """

    if not unit_kerja:
        return None, "Sekretaris Jenderal", "-", "Sekretaris Jenderal"

    # Jika suatu saat UnitKerja punya konfigurasi pejabat SIP Rumah Negara
    pejabat = get_attr(unit_kerja, [
        "pejabat_penerbit_sip_rumah_negara",
        "pejabat_penerbit_sip_rumah",
        "pejabat_penandatangan_sip_rumah",
    ], None)

    jabatan = get_attr(unit_kerja, [
        "nama_jabatan_penerbit_sip_rumah_negara",
        "nama_jabatan_penerbit_sip_rumah",
        "nama_jabatan_penandatangan_sip_rumah",
    ], "")

    if pejabat:
        nama = get_attr(pejabat, ["nama", "nama_pegawai"], "")
        nip = get_attr(pejabat, ["nip"], "")
        jabatan_final = jabatan or get_attr(pejabat, ["jabatan"], "Sekretaris Jenderal")
        return pejabat, nama, nip, jabatan_final

    return None, "Sekretaris Jenderal", "-", "Sekretaris Jenderal"


@transaction.atomic
def run():
    rumah_list = list(Rumah.objects.all())
    pegawai_list = list(Pegawai.objects.all())
    unit_list = list(UnitKerja.objects.all())

    if not rumah_list:
        raise Exception("Master Rumah Negara/Rumah Dinas masih kosong.")

    if not pegawai_list:
        raise Exception("Master Pegawai masih kosong.")

    if not unit_list:
        raise Exception("Master Unit Kerja masih kosong.")

    print(f"Jumlah Rumah Negara tersedia : {len(rumah_list)}")
    print(f"Jumlah Pegawai tersedia      : {len(pegawai_list)}")
    print(f"Jumlah Unit Kerja tersedia   : {len(unit_list)}")
    print(f"Membuat {JUMLAH_DATA} data SIP Rumah Negara random semua unit kerja...")

    status_list = [
        "DRAFT",
        "DIAJUKAN",
        "DITOLAK",
        "TERBIT",
        "BERAKHIR",
    ]

    created_count = 0
    updated_count = 0

    for i in range(1, JUMLAH_DATA + 1):
        rumah = random.choice(rumah_list)
        unit_kerja = get_attr(rumah, ["unit_kerja"], None)

        # Jika rumah belum punya unit kerja, ambil random unit
        if not unit_kerja:
            unit_kerja = random.choice(unit_list)

        pegawai_unit = [
            p for p in pegawai_list
            if get_attr(p, ["unit_kerja"], None) == unit_kerja
        ]

        pegawai = random.choice(pegawai_unit) if pegawai_unit else random.choice(pegawai_list)

        pejabat, nama_pejabat, nip_pejabat, jabatan_pejabat = get_pejabat_penerbit_rumah(unit_kerja)

        nomor_sip = f"SIP-RN-DUMMY-{timezone.now().year}-{i:04d}"

        tanggal_pengajuan = timezone.now() - timedelta(days=random.randint(1, 180))
        tanggal_mulai = tanggal_pengajuan + timedelta(days=random.randint(1, 14))
        tanggal_akhir = tanggal_mulai + timedelta(days=random.randint(365, 730))

        status = random.choice(status_list)

        if status == "DRAFT":
            tanggal_diajukan = None
            tanggal_persetujuan = None
            tanggal_terbit = None
            status_tte = "BELUM"
        elif status == "DIAJUKAN":
            tanggal_diajukan = tanggal_pengajuan + timedelta(days=random.randint(1, 3))
            tanggal_persetujuan = None
            tanggal_terbit = None
            status_tte = "BELUM"
        elif status == "DITOLAK":
            tanggal_diajukan = tanggal_pengajuan + timedelta(days=random.randint(1, 3))
            tanggal_persetujuan = None
            tanggal_terbit = None
            status_tte = "BELUM"
        elif status == "TERBIT":
            tanggal_diajukan = tanggal_pengajuan + timedelta(days=random.randint(1, 3))
            tanggal_persetujuan = tanggal_diajukan + timedelta(days=random.randint(1, 10))
            tanggal_terbit = tanggal_persetujuan + timedelta(days=random.randint(1, 5))
            status_tte = "SUDAH_TTE"
        else:
            tanggal_diajukan = tanggal_pengajuan + timedelta(days=random.randint(1, 3))
            tanggal_persetujuan = tanggal_diajukan + timedelta(days=random.randint(1, 10))
            tanggal_terbit = tanggal_persetujuan + timedelta(days=random.randint(1, 5))
            tanggal_akhir = timezone.now() - timedelta(days=random.randint(1, 365))
            status_tte = "SUDAH_TTE"

        data = {}

        # Nomor SIP
        set_if_exists(data, SIPRumah, "nomor_sip", nomor_sip)
        set_if_exists(data, SIPRumah, "no_sip", nomor_sip)
        set_if_exists(data, SIPRumah, "nomor_surat", nomor_sip)

        # Relasi Rumah Negara
        set_if_exists(data, SIPRumah, "rumah", rumah)
        set_if_exists(data, SIPRumah, "rumah_negara", rumah)
        set_if_exists(data, SIPRumah, "rumah_dinas", rumah)

        # Relasi pegawai/pemohon/penghuni
        set_if_exists(data, SIPRumah, "pegawai", pegawai)
        set_if_exists(data, SIPRumah, "penghuni", pegawai)
        set_if_exists(data, SIPRumah, "pemohon", pegawai)
        set_if_exists(data, SIPRumah, "pemakai", pegawai)
        set_if_exists(data, SIPRumah, "pengguna", pegawai)

        # Unit kerja
        set_if_exists(data, SIPRumah, "unit_kerja", unit_kerja)

        # Tanggal
        set_if_exists(data, SIPRumah, "tanggal_pengajuan", tanggal_pengajuan)
        set_if_exists(data, SIPRumah, "tanggal_diajukan", tanggal_diajukan)
        set_if_exists(data, SIPRumah, "tanggal_persetujuan", tanggal_persetujuan)
        set_if_exists(data, SIPRumah, "tanggal_disetujui", tanggal_persetujuan)
        set_if_exists(data, SIPRumah, "tanggal_mulai", tanggal_mulai)
        set_if_exists(data, SIPRumah, "tanggal_awal", tanggal_mulai)
        set_if_exists(data, SIPRumah, "tanggal_sip", tanggal_mulai)
        set_if_exists(data, SIPRumah, "tanggal_terbit", tanggal_terbit)

        # Masa berlaku
        set_if_exists(data, SIPRumah, "tanggal_akhir", tanggal_akhir)
        set_if_exists(data, SIPRumah, "tanggal_berakhir", tanggal_akhir)
        set_if_exists(data, SIPRumah, "masa_berlaku_sampai", tanggal_akhir)
        set_if_exists(data, SIPRumah, "berlaku_sampai", tanggal_akhir)

        # Status
        set_if_exists(data, SIPRumah, "status", status)
        set_if_exists(data, SIPRumah, "status_tte", status_tte)

        # Keterangan
        set_if_exists(data, SIPRumah, "keperluan", "Penggunaan rumah negara untuk menunjang pelaksanaan tugas kedinasan.")
        set_if_exists(data, SIPRumah, "tujuan_pemakaian", "Penggunaan rumah negara untuk menunjang pelaksanaan tugas kedinasan.")
        set_if_exists(data, SIPRumah, "dasar_penerbitan", "Data dummy pengujian Form SIP Rumah Negara.")
        set_if_exists(data, SIPRumah, "keterangan", "Data dummy Form SIP Rumah Negara untuk semua unit kerja pusat dan UPT.")

        # Snapshot pegawai/penghuni
        nama_pegawai = get_attr(pegawai, ["nama", "nama_pegawai"], "")
        nip_pegawai = get_attr(pegawai, ["nip"], "")
        jabatan_pegawai = get_attr(pegawai, ["jabatan"], "")

        set_if_exists(data, SIPRumah, "nama_penghuni", nama_pegawai)
        set_if_exists(data, SIPRumah, "nip_penghuni", nip_pegawai)
        set_if_exists(data, SIPRumah, "jabatan_penghuni", jabatan_pegawai)

        set_if_exists(data, SIPRumah, "nama_pemohon", nama_pegawai)
        set_if_exists(data, SIPRumah, "nip_pemohon", nip_pegawai)
        set_if_exists(data, SIPRumah, "jabatan_pemohon", jabatan_pegawai)

        set_if_exists(data, SIPRumah, "nama_pengguna", nama_pegawai)
        set_if_exists(data, SIPRumah, "nip_pengguna", nip_pegawai)
        set_if_exists(data, SIPRumah, "jabatan_pengguna", jabatan_pegawai)

        # Snapshot pejabat penandatangan SIP Rumah Negara
        if pejabat:
            set_if_exists(data, SIPRumah, "pejabat_penerbit", pejabat)
            set_if_exists(data, SIPRumah, "pejabat_penandatangan", pejabat)
            set_if_exists(data, SIPRumah, "diajukan_kepada", pejabat)

        set_if_exists(data, SIPRumah, "nama_pejabat_penerbit", nama_pejabat)
        set_if_exists(data, SIPRumah, "nip_pejabat_penerbit", nip_pejabat)
        set_if_exists(data, SIPRumah, "jabatan_pejabat_penerbit", jabatan_pejabat)

        set_if_exists(data, SIPRumah, "nama_pejabat_penandatangan", nama_pejabat)
        set_if_exists(data, SIPRumah, "nip_pejabat_penandatangan", nip_pejabat)
        set_if_exists(data, SIPRumah, "jabatan_pejabat_penandatangan", jabatan_pejabat)

        if status == "DITOLAK":
            set_if_exists(data, SIPRumah, "catatan_penolakan", "Data dummy ditolak untuk pengujian revisi SIP Rumah Negara.")

        if status == "TERBIT":
            set_if_exists(data, SIPRumah, "catatan_persetujuan", "Data dummy SIP Rumah Negara sudah terbit.")

        lookup_field = get_lookup_field(SIPRumah, [
            "nomor_sip",
            "no_sip",
            "nomor_surat",
        ])

        if lookup_field:
            obj, created = SIPRumah.objects.update_or_create(
                **{lookup_field: nomor_sip},
                defaults=data
            )
        else:
            obj = SIPRumah.objects.create(**data)
            created = True

        if created:
            created_count += 1
        else:
            updated_count += 1

    print("")
    print("SELESAI.")
    print(f"Data SIP Rumah Negara dibuat baru : {created_count}")
    print(f"Data SIP Rumah Negara diupdate    : {updated_count}")
    print(f"Total diproses                    : {JUMLAH_DATA}")
    print("")
    print("Data tersebar random ke semua unit kerja pusat dan UPT berdasarkan master Rumah Negara.")


run()