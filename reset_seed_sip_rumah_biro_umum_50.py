import random
from datetime import timedelta
from django.apps import apps
from django.db import transaction
from django.utils import timezone


JUMLAH_DATA = 50
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


def get_lookup_field(model, fields):
    for field in fields:
        if has_field(model, field):
            return field
    return None


def find_unit_biro_umum():
    for unit in UnitKerja.objects.all():
        nama = get_unit_name(unit).upper()
        if "BIRO UMUM" in nama:
            return unit

    raise Exception("Unit kerja Biro Umum tidak ditemukan. Pastikan Master Unit Kerja Biro Umum sudah ada.")


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
    print("Menghapus semua data SIP Rumah Negara...")

    deleted_count, deleted_detail = SIPRumah.objects.all().delete()

    print(f"Data SIP Rumah Negara terhapus: {deleted_count}")
    print(deleted_detail)

    unit_biro_umum = find_unit_biro_umum()

    rumah_list = list(Rumah.objects.filter(unit_kerja=unit_biro_umum))
    pegawai_list = list(Pegawai.objects.filter(unit_kerja=unit_biro_umum))

    if not rumah_list:
        raise Exception("Data master Rumah Negara untuk Biro Umum masih kosong.")

    if not pegawai_list:
        raise Exception("Data master Pegawai untuk Biro Umum masih kosong.")

    print("")
    print(f"Unit kerja             : {get_unit_name(unit_biro_umum)}")
    print(f"Rumah Negara tersedia  : {len(rumah_list)}")
    print(f"Pegawai tersedia       : {len(pegawai_list)}")
    print(f"Membuat {JUMLAH_DATA} SIP Rumah Negara status DRAFT...")

    created_count = 0

    for i in range(1, JUMLAH_DATA + 1):
        rumah = random.choice(rumah_list)
        pegawai = random.choice(pegawai_list)

        nomor_sip = f"SIP-RN-DRAFT-BU-{timezone.now().year}-{i:04d}"

        tanggal_sip = timezone.now() - timedelta(days=random.randint(1, 30))
        tanggal_mulai = tanggal_sip
        tanggal_akhir = tanggal_mulai + timedelta(days=random.randint(365, 730))

        data = {}

        # Nomor SIP
        set_if_exists(data, SIPRumah, "nomor_sip", nomor_sip)
        set_if_exists(data, SIPRumah, "no_sip", nomor_sip)
        set_if_exists(data, SIPRumah, "nomor_surat", nomor_sip)

        # Relasi rumah
        set_if_exists(data, SIPRumah, "rumah", rumah)
        set_if_exists(data, SIPRumah, "rumah_negara", rumah)
        set_if_exists(data, SIPRumah, "rumah_dinas", rumah)

        # Relasi pegawai/calon pengguna/pemegang SIP
        set_if_exists(data, SIPRumah, "pegawai", pegawai)
        set_if_exists(data, SIPRumah, "penghuni", pegawai)
        set_if_exists(data, SIPRumah, "pemohon", pegawai)
        set_if_exists(data, SIPRumah, "pemakai", pegawai)
        set_if_exists(data, SIPRumah, "pengguna", pegawai)
        set_if_exists(data, SIPRumah, "pemegang_sip", pegawai)
        set_if_exists(data, SIPRumah, "penghuni_aktual", pegawai)

        # Unit kerja
        set_if_exists(data, SIPRumah, "unit_kerja", unit_biro_umum)

        # Tanggal
        set_if_exists(data, SIPRumah, "tanggal_sip", tanggal_sip)
        set_if_exists(data, SIPRumah, "tanggal_pengajuan", tanggal_sip)
        set_if_exists(data, SIPRumah, "tanggal_mulai", tanggal_mulai)
        set_if_exists(data, SIPRumah, "tanggal_awal", tanggal_mulai)
        set_if_exists(data, SIPRumah, "tanggal_terbit", None)

        # Masa berlaku
        set_if_exists(data, SIPRumah, "tanggal_akhir", tanggal_akhir)
        set_if_exists(data, SIPRumah, "tanggal_berakhir", tanggal_akhir)
        set_if_exists(data, SIPRumah, "masa_berlaku_sampai", tanggal_akhir)
        set_if_exists(data, SIPRumah, "berlaku_sampai", tanggal_akhir)

        # Status alur baru
        set_if_exists(data, SIPRumah, "status", "DRAFT")
        set_if_exists(data, SIPRumah, "status_tte", "BELUM")
        set_if_exists(data, SIPRumah, "status_tte_calon_pengguna", "BELUM")

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
            "jenis_masa_berlaku",
            "Selama Masih Menduduki Jabatan"
        )
        set_if_exists(data, SIPRumah, "dasar_penerbitan", "Draft dummy SIP Rumah Negara Biro Umum.")
        set_if_exists(data, SIPRumah, "keterangan", "Data dummy DRAFT SIP Rumah Negara unit Biro Umum.")

        # Snapshot calon pengguna rumah
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

        set_if_exists(data, SIPRumah, "nama_pemegang_sip", nama_pegawai)
        set_if_exists(data, SIPRumah, "nip_pemegang_sip", nip_pegawai)
        set_if_exists(data, SIPRumah, "jabatan_pemegang_sip", jabatan_pegawai)

        # Pejabat penandatangan SIP Rumah Negara
        set_if_exists(data, SIPRumah, "jabatan_pejabat_penerbit", "Sekretaris Jenderal")
        set_if_exists(data, SIPRumah, "jabatan_pejabat_penandatangan", "Sekretaris Jenderal")
        set_if_exists(data, SIPRumah, "nama_pejabat_penerbit", "Sekretaris Jenderal")
        set_if_exists(data, SIPRumah, "nama_pejabat_penandatangan", "Sekretaris Jenderal")
        set_if_exists(data, SIPRumah, "nip_pejabat_penerbit", "-")
        set_if_exists(data, SIPRumah, "nip_pejabat_penandatangan", "-")

        SIPRumah.objects.create(**data)
        created_count += 1

    print("")
    print("SELESAI.")
    print("Data SIP Rumah Negara lama sudah dihapus.")
    print(f"Data SIP Rumah Negara DRAFT Biro Umum dibuat: {created_count}")


run()