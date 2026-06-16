import random
from datetime import timedelta
from django.apps import apps
from django.db import transaction
from django.utils import timezone


JUMLAH_DATA = 10
NAMA_UNIT = "Biro Umum"


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


def find_unit_biro_umum():
    for unit in UnitKerja.objects.all():
        nama = get_unit_name(unit).upper()
        if "BIRO UMUM" in nama:
            return unit

    raise Exception("Unit kerja Biro Umum tidak ditemukan. Pastikan Master Unit Kerja Biro Umum sudah ada.")


def get_lookup_field(model, fields):
    for field in fields:
        if has_field(model, field):
            return field
    return None


UnitKerja = get_model("master", ["UnitKerja"])
Pegawai = get_model("master", ["Pegawai"])
Rumah = get_model("master", ["RumahNegara", "RumahDinas"])

SIPRumah = get_model("rumah_dinas", [
    "SIPRumahNegara",
    "SipRumahNegara",
    "SIPRumahDinas",
    "SipRumahDinas",
])


@transaction.atomic
def run():
    unit_biro_umum = find_unit_biro_umum()

    rumah_list = list(
        Rumah.objects.filter(unit_kerja=unit_biro_umum)
    )

    pegawai_list = list(
        Pegawai.objects.filter(unit_kerja=unit_biro_umum)
    )

    if not rumah_list:
        raise Exception("Data master Rumah Negara untuk Biro Umum masih kosong.")

    if not pegawai_list:
        raise Exception("Data master Pegawai untuk Biro Umum masih kosong.")

    print(f"Unit kerja             : {get_unit_name(unit_biro_umum)}")
    print(f"Rumah Negara tersedia  : {len(rumah_list)}")
    print(f"Pegawai tersedia       : {len(pegawai_list)}")

    status_list = [
        "DRAFT",
        "DIAJUKAN",
        "TERBIT",
        "DITOLAK",
    ]

    created_count = 0
    updated_count = 0

    for i in range(1, JUMLAH_DATA + 1):
        rumah = random.choice(rumah_list)
        pegawai = random.choice(pegawai_list)

        nomor_sip = f"SIP-RN-BU-{timezone.now().year}-{i:04d}"

        tanggal_sip = timezone.now() - timedelta(days=random.randint(1, 60))
        tanggal_mulai = tanggal_sip
        tanggal_akhir = tanggal_mulai + timedelta(days=random.randint(365, 730))

        status = random.choice(status_list)

        data = {}

        # Nomor SIP
        set_if_exists(data, SIPRumah, "nomor_sip", nomor_sip)
        set_if_exists(data, SIPRumah, "no_sip", nomor_sip)
        set_if_exists(data, SIPRumah, "nomor_surat", nomor_sip)

        # Relasi rumah
        set_if_exists(data, SIPRumah, "rumah", rumah)
        set_if_exists(data, SIPRumah, "rumah_negara", rumah)
        set_if_exists(data, SIPRumah, "rumah_dinas", rumah)

        # Relasi pegawai/penghuni/pemohon
        set_if_exists(data, SIPRumah, "pegawai", pegawai)
        set_if_exists(data, SIPRumah, "penghuni", pegawai)
        set_if_exists(data, SIPRumah, "pemohon", pegawai)
        set_if_exists(data, SIPRumah, "pemakai", pegawai)
        set_if_exists(data, SIPRumah, "pengguna", pegawai)

        # Unit kerja
        set_if_exists(data, SIPRumah, "unit_kerja", unit_biro_umum)

        # Tanggal
        set_if_exists(data, SIPRumah, "tanggal_sip", tanggal_sip)
        set_if_exists(data, SIPRumah, "tanggal_pengajuan", tanggal_sip)
        set_if_exists(data, SIPRumah, "tanggal_mulai", tanggal_mulai)
        set_if_exists(data, SIPRumah, "tanggal_awal", tanggal_mulai)
        set_if_exists(data, SIPRumah, "tanggal_terbit", tanggal_mulai)

        # Masa berlaku
        set_if_exists(data, SIPRumah, "tanggal_akhir", tanggal_akhir)
        set_if_exists(data, SIPRumah, "tanggal_berakhir", tanggal_akhir)
        set_if_exists(data, SIPRumah, "masa_berlaku_sampai", tanggal_akhir)
        set_if_exists(data, SIPRumah, "berlaku_sampai", tanggal_akhir)

        # Status
        set_if_exists(data, SIPRumah, "status", status)
        set_if_exists(data, SIPRumah, "status_tte", "BELUM")

        # Keterangan
        set_if_exists(
            data,
            SIPRumah,
            "keperluan",
            "Penggunaan rumah negara untuk menunjang pelaksanaan tugas kedinasan."
        )
        set_if_exists(
            data,
            SIPRumah,
            "tujuan_penggunaan",
            "Penggunaan rumah negara untuk menunjang pelaksanaan tugas kedinasan."
        )
        set_if_exists(
            data,
            SIPRumah,
            "keterangan",
            "Data dummy Form SIP Rumah Negara unit Biro Umum."
        )

        # Snapshot penghuni/pemohon
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

        # Pejabat penerbit/penandatangan SIP Rumah Negara
        set_if_exists(data, SIPRumah, "jabatan_pejabat_penerbit", "Sekretaris Jenderal")
        set_if_exists(data, SIPRumah, "jabatan_pejabat_penandatangan", "Sekretaris Jenderal")
        set_if_exists(data, SIPRumah, "nama_pejabat_penerbit", "Sekretaris Jenderal")
        set_if_exists(data, SIPRumah, "nama_pejabat_penandatangan", "Sekretaris Jenderal")
        set_if_exists(data, SIPRumah, "nip_pejabat_penerbit", "-")
        set_if_exists(data, SIPRumah, "nip_pejabat_penandatangan", "-")

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
    print(f"Data SIP Rumah Negara Biro Umum dibuat baru : {created_count}")
    print(f"Data SIP Rumah Negara Biro Umum diupdate    : {updated_count}")
    print(f"Total diproses                              : {JUMLAH_DATA}")


run()