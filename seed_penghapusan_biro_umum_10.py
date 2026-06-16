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
PermohonanPenghapusan = get_model("penghapusan", [
    "PermohonanPenghapusanBMN",
    "PermohonanPenghapusan",
    "PenghapusanBMN",
])


# Model detail barang penghapusan, jika tersedia
try:
    DetailBarangPenghapusan = get_model("penghapusan", [
        "DetailBarangPenghapusanBMN",
        "BarangPenghapusanBMN",
        "DetailPenghapusanBMN",
        "ItemPenghapusanBMN",
    ])
except LookupError:
    DetailBarangPenghapusan = None


@transaction.atomic
def run():
    unit_biro_umum = find_unit_biro_umum()

    pegawai_list = list(Pegawai.objects.filter(unit_kerja=unit_biro_umum))

    if not pegawai_list:
        raise Exception("Data master Pegawai untuk Biro Umum masih kosong. Buat seed pegawai Biro Umum terlebih dahulu.")

    print(f"Unit kerja digunakan : {get_unit_name(unit_biro_umum)}")
    print(f"Pegawai tersedia     : {len(pegawai_list)}")
    print(f"Membuat {JUMLAH_DATA} permohonan penghapusan BMN Biro Umum...")

    jenis_barang_list = [
        "Peralatan dan Mesin",
        "BMN Lainnya",
        "Aset Tetap Lainnya",
    ]

    status_list = [
        "DIAJUKAN_UNIT_KERJA",
        "MENUNGGU_VERIFIKASI_BIRO_UMUM",
        "DIVERIFIKASI_BIRO_UMUM",
        "DIAJUKAN_KE_SEKJEN",
        "PERLU_PERBAIKAN",
    ]

    alasan_list = [
        "Barang rusak berat dan tidak ekonomis untuk diperbaiki.",
        "Barang sudah tidak mendukung kebutuhan operasional.",
        "Barang telah melewati masa manfaat dan perlu dihapuskan.",
        "Barang dalam kondisi usang dan tidak dapat dimanfaatkan optimal.",
        "Barang hilang/rusak berdasarkan hasil pemeriksaan internal.",
    ]

    created_count = 0
    updated_count = 0
    detail_created_count = 0

    for i in range(1, JUMLAH_DATA + 1):
        pegawai = random.choice(pegawai_list)

        tanggal_permohonan = timezone.now().date() - timedelta(days=random.randint(1, 30))
        nomor_permohonan = f"PH-BU-{timezone.now().year}-{i:04d}"

        jumlah_barang = random.randint(3, 15)
        nilai_total = random.randint(5_000_000, 150_000_000)

        data = {}

        # Nomor dan tanggal
        set_if_exists(data, PermohonanPenghapusan, "nomor_permohonan", nomor_permohonan)
        set_if_exists(data, PermohonanPenghapusan, "nomor_usulan", nomor_permohonan)
        set_if_exists(data, PermohonanPenghapusan, "nomor_surat", nomor_permohonan)
        set_if_exists(data, PermohonanPenghapusan, "tanggal_permohonan", tanggal_permohonan)
        set_if_exists(data, PermohonanPenghapusan, "tanggal_usulan", tanggal_permohonan)
        set_if_exists(data, PermohonanPenghapusan, "tanggal_surat", tanggal_permohonan)

        # Unit dan pemohon
        set_if_exists(data, PermohonanPenghapusan, "unit_kerja", unit_biro_umum)
        set_if_exists(data, PermohonanPenghapusan, "unit_kerja_pemohon", unit_biro_umum)
        set_if_exists(data, PermohonanPenghapusan, "pegawai_pemohon", pegawai)
        set_if_exists(data, PermohonanPenghapusan, "pemohon", pegawai)
        set_if_exists(data, PermohonanPenghapusan, "pic_unit_kerja", pegawai)

        # Snapshot pemohon
        nama_pegawai = get_attr(pegawai, ["nama", "nama_pegawai"], "")
        nip_pegawai = get_attr(pegawai, ["nip"], "")
        jabatan_pegawai = get_attr(pegawai, ["jabatan"], "")

        set_if_exists(data, PermohonanPenghapusan, "nama_pemohon", nama_pegawai)
        set_if_exists(data, PermohonanPenghapusan, "nip_pemohon", nip_pegawai)
        set_if_exists(data, PermohonanPenghapusan, "jabatan_pemohon", jabatan_pegawai)

        # Judul dan uraian
        judul = f"Permohonan Penghapusan BMN Biro Umum Paket {i:03d}"
        set_if_exists(data, PermohonanPenghapusan, "judul", judul)
        set_if_exists(data, PermohonanPenghapusan, "judul_permohonan", judul)
        set_if_exists(data, PermohonanPenghapusan, "nama_paket", judul)
        set_if_exists(data, PermohonanPenghapusan, "paket", judul)

        jenis_barang = random.choice(jenis_barang_list)
        alasan = random.choice(alasan_list)

        set_if_exists(data, PermohonanPenghapusan, "jenis_barang", jenis_barang)
        set_if_exists(data, PermohonanPenghapusan, "jenis_aset", jenis_barang)
        set_if_exists(data, PermohonanPenghapusan, "jumlah_barang", jumlah_barang)
        set_if_exists(data, PermohonanPenghapusan, "total_nilai", nilai_total)
        set_if_exists(data, PermohonanPenghapusan, "nilai_perolehan", nilai_total)
        set_if_exists(data, PermohonanPenghapusan, "nilai_total_perolehan", nilai_total)

        set_if_exists(data, PermohonanPenghapusan, "alasan_penghapusan", alasan)
        set_if_exists(data, PermohonanPenghapusan, "alasan", alasan)
        set_if_exists(data, PermohonanPenghapusan, "keterangan", alasan)
        set_if_exists(data, PermohonanPenghapusan, "uraian", alasan)

        # Status alur baru
        status = random.choice(status_list)
        set_if_exists(data, PermohonanPenghapusan, "status", status)
        set_if_exists(data, PermohonanPenghapusan, "status_permohonan", status)

        # Catatan proses
        set_if_exists(data, PermohonanPenghapusan, "catatan", "Data dummy permohonan penghapusan BMN Biro Umum.")
        set_if_exists(data, PermohonanPenghapusan, "catatan_biro_umum", "Menunggu/verifikasi awal Biro Umum.")
        set_if_exists(data, PermohonanPenghapusan, "catatan_sekjen", "")

        lookup_field = get_lookup_field(PermohonanPenghapusan, [
            "nomor_permohonan",
            "nomor_usulan",
            "nomor_surat",
        ])

        if lookup_field:
            obj, created = PermohonanPenghapusan.objects.update_or_create(
                **{lookup_field: data.get(lookup_field)},
                defaults=data
            )
        else:
            obj = PermohonanPenghapusan.objects.create(**data)
            created = True

        if created:
            created_count += 1
        else:
            updated_count += 1

        # Buat detail barang jika model detail tersedia
        if DetailBarangPenghapusan:
            for n in range(1, jumlah_barang + 1):
                detail_data = {}

                set_if_exists(detail_data, DetailBarangPenghapusan, "permohonan", obj)
                set_if_exists(detail_data, DetailBarangPenghapusan, "permohonan_penghapusan", obj)
                set_if_exists(detail_data, DetailBarangPenghapusan, "penghapusan", obj)

                set_if_exists(detail_data, DetailBarangPenghapusan, "kode_barang", f"3100102{random.randint(1000,9999)}")
                set_if_exists(detail_data, DetailBarangPenghapusan, "nup", f"{i:03d}{n:04d}")
                set_if_exists(detail_data, DetailBarangPenghapusan, "nama_barang", f"Barang Penghapusan Biro Umum {i:03d}-{n:03d}")
                set_if_exists(detail_data, DetailBarangPenghapusan, "merk_tipe", random.choice(["Acer", "Lenovo", "HP", "Canon", "Epson", "Panasonic"]))
                set_if_exists(detail_data, DetailBarangPenghapusan, "tipe", random.choice(["Laptop", "Printer", "Scanner", "Meja Kerja", "Kursi Kerja"]))
                set_if_exists(detail_data, DetailBarangPenghapusan, "tahun_perolehan", random.randint(2010, 2020))
                set_if_exists(detail_data, DetailBarangPenghapusan, "qty", 1)
                set_if_exists(detail_data, DetailBarangPenghapusan, "jumlah", 1)
                set_if_exists(detail_data, DetailBarangPenghapusan, "nilai_perolehan", int(nilai_total / jumlah_barang))
                set_if_exists(detail_data, DetailBarangPenghapusan, "kondisi", "Rusak Berat")
                set_if_exists(detail_data, DetailBarangPenghapusan, "keterangan", "Dummy barang penghapusan BMN Biro Umum.")

                DetailBarangPenghapusan.objects.create(**detail_data)
                detail_created_count += 1

    print("")
    print("SELESAI.")
    print(f"Permohonan Penghapusan dibuat baru : {created_count}")
    print(f"Permohonan Penghapusan diupdate    : {updated_count}")
    print(f"Detail barang dibuat               : {detail_created_count}")
    print(f"Total permohonan diproses          : {JUMLAH_DATA}")


run()