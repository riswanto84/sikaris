import random
from datetime import timedelta
from django.apps import apps
from django.db import transaction
from django.utils import timezone


JUMLAH_DATA = 100


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
Kendaraan = get_model("master", ["Kendaraan"])
SIPKendaraan = get_model("kendaraan", ["SIPKendaraan", "SipKendaraan"])


def get_pejabat_penerbit(unit_kerja):
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
    nama_unit = get_unit_name(unit_kerja).upper()

    # Fallback Biro Umum untuk Setjen
    if "SEKRETARIAT JENDERAL" in str(unit_eselon_i).upper() or "BIRO UMUM" in nama_unit:
        for u in UnitKerja.objects.all():
            if "BIRO UMUM" in get_unit_name(u).upper():
                pejabat = get_attr(u, ["pejabat_penerbit_sip_kendaraan"], None)
                jabatan = get_attr(u, ["nama_jabatan_penerbit_sip_kendaraan"], "")
                if pejabat:
                    return (
                        pejabat,
                        get_attr(pejabat, ["nama", "nama_pegawai"], ""),
                        get_attr(pejabat, ["nip"], ""),
                        jabatan or get_attr(pejabat, ["jabatan"], "Kepala Biro Umum"),
                    )

    # Fallback sekretariat eselon I
    if unit_eselon_i:
        for u in UnitKerja.objects.all():
            u_eselon = get_attr(u, ["unit_eselon_i", "nama_eselon_i"], "")
            u_nama = get_unit_name(u).upper()

            if u_eselon == unit_eselon_i and "SEKRETARIAT" in u_nama:
                pejabat = get_attr(u, ["pejabat_penerbit_sip_kendaraan"], None)
                jabatan = get_attr(u, ["nama_jabatan_penerbit_sip_kendaraan"], "")
                if pejabat:
                    return (
                        pejabat,
                        get_attr(pejabat, ["nama", "nama_pegawai"], ""),
                        get_attr(pejabat, ["nip"], ""),
                        jabatan or get_attr(pejabat, ["jabatan"], ""),
                    )

    return None, "", "", ""


@transaction.atomic
def run():
    print("Menghapus semua data SIP Kendaraan...")

    deleted_count, deleted_detail = SIPKendaraan.objects.all().delete()

    print(f"Data SIP Kendaraan terhapus: {deleted_count}")
    print(deleted_detail)

    kendaraan_list = list(Kendaraan.objects.all())
    pegawai_list = list(Pegawai.objects.all())

    if not kendaraan_list:
        raise Exception("Master kendaraan masih kosong. Buat data kendaraan terlebih dahulu.")

    if not pegawai_list:
        raise Exception("Master pegawai masih kosong. Buat data pegawai terlebih dahulu.")

    print(f"Jumlah kendaraan tersedia : {len(kendaraan_list)}")
    print(f"Jumlah pegawai tersedia   : {len(pegawai_list)}")
    print(f"Membuat {JUMLAH_DATA} SIP Kendaraan status DRAFT...")

    created_count = 0
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

        pejabat, nama_pejabat, nip_pejabat, jabatan_pejabat = get_pejabat_penerbit(unit_kerja)

        if not pejabat:
            tanpa_pejabat_count += 1

        nomor_sip = f"SIP-DRAFT-{timezone.now().year}-{i:04d}"

        tanggal_sip = timezone.now() - timedelta(days=random.randint(1, 30))
        tanggal_mulai = tanggal_sip
        tanggal_akhir = tanggal_mulai + timedelta(days=365)

        data = {}

        # Nomor SIP
        set_if_exists(data, SIPKendaraan, "nomor_sip", nomor_sip)
        set_if_exists(data, SIPKendaraan, "no_sip", nomor_sip)
        set_if_exists(data, SIPKendaraan, "nomor_surat", nomor_sip)

        # Relasi kendaraan dan pegawai
        set_if_exists(data, SIPKendaraan, "kendaraan", kendaraan)
        set_if_exists(data, SIPKendaraan, "pegawai", pegawai)
        set_if_exists(data, SIPKendaraan, "pengguna", pegawai)
        set_if_exists(data, SIPKendaraan, "pemegang", pegawai)
        set_if_exists(data, SIPKendaraan, "pemakai", pegawai)
        set_if_exists(data, SIPKendaraan, "unit_kerja", unit_kerja)

        # Tanggal
        set_if_exists(data, SIPKendaraan, "tanggal_sip", tanggal_sip)
        set_if_exists(data, SIPKendaraan, "tanggal_pengajuan", tanggal_sip)
        set_if_exists(data, SIPKendaraan, "tanggal_mulai", tanggal_mulai)
        set_if_exists(data, SIPKendaraan, "tanggal_awal", tanggal_mulai)
        set_if_exists(data, SIPKendaraan, "tanggal_akhir", tanggal_akhir)
        set_if_exists(data, SIPKendaraan, "tanggal_berakhir", tanggal_akhir)
        set_if_exists(data, SIPKendaraan, "masa_berlaku_sampai", tanggal_akhir)
        set_if_exists(data, SIPKendaraan, "berlaku_sampai", tanggal_akhir)

        # Status wajib DRAFT
        set_if_exists(data, SIPKendaraan, "status", "DRAFT")
        set_if_exists(data, SIPKendaraan, "status_tte", "BELUM")
        set_if_exists(data, SIPKendaraan, "status_tte_pengusul", "BELUM")

        # Informasi penggunaan
        set_if_exists(data, SIPKendaraan, "tujuan_pemakaian", "Menunjang pelaksanaan tugas kedinasan.")
        set_if_exists(data, SIPKendaraan, "keperluan", "Menunjang pelaksanaan tugas kedinasan.")
        set_if_exists(data, SIPKendaraan, "lokasi_penggunaan", "DKI Jakarta")
        set_if_exists(data, SIPKendaraan, "dasar_penerbitan", "Draft dummy SIP Kendaraan.")
        set_if_exists(data, SIPKendaraan, "keterangan", "Data dummy draft SIP Kendaraan.")

        # Snapshot pegawai calon pemegang SIP
        set_if_exists(data, SIPKendaraan, "nama_pengguna", get_attr(pegawai, ["nama", "nama_pegawai"], ""))
        set_if_exists(data, SIPKendaraan, "nip_pengguna", get_attr(pegawai, ["nip"], ""))
        set_if_exists(data, SIPKendaraan, "jabatan_pengguna", get_attr(pegawai, ["jabatan"], ""))

        # Pejabat penerbit
        if pejabat:
            set_if_exists(data, SIPKendaraan, "diajukan_kepada", pejabat)
            set_if_exists(data, SIPKendaraan, "pejabat_penerbit", pejabat)

        set_if_exists(data, SIPKendaraan, "nama_pejabat_penerbit", nama_pejabat)
        set_if_exists(data, SIPKendaraan, "nip_pejabat_penerbit", nip_pejabat)
        set_if_exists(data, SIPKendaraan, "jabatan_pejabat_penerbit", jabatan_pejabat)

        set_if_exists(data, SIPKendaraan, "nama_pejabat_penandatangan", nama_pejabat)
        set_if_exists(data, SIPKendaraan, "nip_pejabat_penandatangan", nip_pejabat)
        set_if_exists(data, SIPKendaraan, "jabatan_pejabat_penandatangan", jabatan_pejabat)

        SIPKendaraan.objects.create(**data)
        created_count += 1

    print("")
    print("SELESAI.")
    print(f"Data SIP Kendaraan lama dihapus.")
    print(f"Data SIP Kendaraan DRAFT dibuat: {created_count}")
    print(f"Data tanpa pejabat penerbit    : {tanpa_pejabat_count}")
    print("")
    print("Silakan buka menu Daftar SIP Kendaraan.")


run()