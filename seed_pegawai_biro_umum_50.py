import random
from django.apps import apps
from django.db import transaction


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


def find_or_create_biro_umum():
    # Cari Biro Umum yang sudah ada
    for unit in UnitKerja.objects.all():
        nama = get_unit_name(unit).upper()
        if "BIRO UMUM" in nama:
            return unit

    # Kalau belum ada, buat baru
    data = {}

    set_if_exists(data, UnitKerja, "nama_unit", NAMA_UNIT)
    set_if_exists(data, UnitKerja, "nama", NAMA_UNIT)
    set_if_exists(data, UnitKerja, "nama_unit_kerja", NAMA_UNIT)
    set_if_exists(data, UnitKerja, "kode_unit", "BU")
    set_if_exists(data, UnitKerja, "kode", "BU")
    set_if_exists(data, UnitKerja, "jenis_unit", "SETJEN")
    set_if_exists(data, UnitKerja, "unit_eselon_i", "Sekretariat Jenderal")
    set_if_exists(data, UnitKerja, "nama_eselon_i", "Sekretariat Jenderal")
    set_if_exists(data, UnitKerja, "alamat", "Jl. Salemba Raya No. 28, Jakarta Pusat")
    set_if_exists(data, UnitKerja, "keterangan", "Unit kerja Biro Umum Sekretariat Jenderal")

    return UnitKerja.objects.create(**data)


def get_lookup_field(model, fields):
    for field in fields:
        if has_field(model, field):
            return field
    return None


UnitKerja = get_model("master", ["UnitKerja"])
Pegawai = get_model("master", ["Pegawai"])


@transaction.atomic
def run():
    unit_biro_umum = find_or_create_biro_umum()

    print(f"Unit kerja digunakan: {get_unit_name(unit_biro_umum)}")

    nama_depan = [
        "Ahmad", "Agus", "Andi", "Arif", "Budi", "Citra", "Dedi", "Dewi",
        "Eka", "Fajar", "Hendra", "Indah", "Joko", "Kartika", "Lestari",
        "Maya", "Nurul", "Putri", "Rizky", "Sari", "Taufik", "Utami",
        "Wahyu", "Yuni", "Zainal"
    ]

    nama_belakang = [
        "Pratama", "Saputra", "Wijaya", "Santoso", "Permana", "Hidayat",
        "Maulana", "Kusuma", "Ramadhan", "Purnama", "Setiawan",
        "Firmansyah", "Laksana", "Kurniawan", "Wibowo", "Nugraha"
    ]

    jabatan_list = [
        "Kepala Biro Umum",
        "Kepala Bagian Rumah Tangga",
        "Kepala Bagian Perlengkapan dan BMN",
        "Kepala Subbagian Perlengkapan",
        "Kepala Subbagian BMN",
        "Analis Barang Milik Negara",
        "Pengelola Barang Milik Negara",
        "Pengadministrasi Umum",
        "Pranata Komputer Ahli Pertama",
        "Analis Kebijakan Ahli Pertama",
        "Analis Kebijakan Ahli Muda",
        "Arsiparis Ahli Pertama",
        "Perencana Ahli Pertama",
        "Penyusun Bahan Laporan",
        "Pengolah Data",
        "Pengelola Keuangan",
    ]

    pangkat_list = [
        "Pengatur / II-c",
        "Pengatur Tk. I / II-d",
        "Penata Muda / III-a",
        "Penata Muda Tk. I / III-b",
        "Penata / III-c",
        "Penata Tk. I / III-d",
        "Pembina / IV-a",
        "Pembina Tk. I / IV-b",
    ]

    golongan_list = [
        "II/c", "II/d", "III/a", "III/b", "III/c", "III/d", "IV/a", "IV/b"
    ]

    created_count = 0
    updated_count = 0

    for i in range(1, JUMLAH_DATA + 1):
        nip = f"197{random.randint(0,9)}{random.randint(1,12):02d}{random.randint(1,28):02d}20{random.randint(10,24):02d}{random.randint(1,2)}{i:04d}"
        nama = f"{random.choice(nama_depan)} {random.choice(nama_belakang)} Biro Umum {i:03d}"

        data = {}

        set_if_exists(data, Pegawai, "nip", nip)
        set_if_exists(data, Pegawai, "nik", f"3173{random.randint(100000000000,999999999999)}")
        set_if_exists(data, Pegawai, "nama", nama)
        set_if_exists(data, Pegawai, "nama_pegawai", nama)
        set_if_exists(data, Pegawai, "jabatan", random.choice(jabatan_list))
        set_if_exists(data, Pegawai, "pangkat", random.choice(pangkat_list))
        set_if_exists(data, Pegawai, "golongan", random.choice(golongan_list))
        set_if_exists(data, Pegawai, "email", f"pegawai.biroumum{i:03d}@kemsos.go.id")
        set_if_exists(data, Pegawai, "no_hp", f"0812{random.randint(10000000,99999999)}")
        set_if_exists(data, Pegawai, "alamat", "Jakarta Pusat")
        set_if_exists(data, Pegawai, "status", "Aktif")
        set_if_exists(data, Pegawai, "status_pegawai", "Aktif")
        set_if_exists(data, Pegawai, "unit_kerja", unit_biro_umum)

        lookup_field = get_lookup_field(Pegawai, ["nip", "email", "nama", "nama_pegawai"])

        if not lookup_field:
            raise Exception("Tidak ditemukan field lookup pada model Pegawai.")

        obj, created = Pegawai.objects.update_or_create(
            **{lookup_field: data.get(lookup_field)},
            defaults=data
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    print("")
    print("SELESAI.")
    print(f"Pegawai Biro Umum dibuat baru : {created_count}")
    print(f"Pegawai Biro Umum diupdate    : {updated_count}")
    print(f"Total diproses                : {JUMLAH_DATA}")


run()