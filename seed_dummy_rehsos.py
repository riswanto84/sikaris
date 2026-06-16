import random
from datetime import date, timedelta
from django.apps import apps
from django.db import transaction


UNIT_KERJA_NAMA = "Sekretariat Direktorat Jenderal Rehabilitasi Sosial"
JUMLAH_DATA = 50


def get_model(app_label, model_names):
    for name in model_names:
        try:
            return apps.get_model(app_label, name)
        except LookupError:
            continue
    raise LookupError(f"Model tidak ditemukan: {app_label}.{model_names}")


UnitKerja = get_model("master", ["UnitKerja"])
Pegawai = get_model("master", ["Pegawai"])
Kendaraan = get_model("master", ["Kendaraan"])
Rumah = get_model("master", ["RumahNegara", "RumahDinas"])


def has_field(model, field_name):
    return any(f.name == field_name for f in model._meta.fields)


def set_if_exists(data, model, field_name, value):
    if has_field(model, field_name):
        data[field_name] = value


def get_or_create_unit_kerja():
    data = {}

    if has_field(UnitKerja, "nama_unit"):
        lookup = {"nama_unit": UNIT_KERJA_NAMA}
    elif has_field(UnitKerja, "nama"):
        lookup = {"nama": UNIT_KERJA_NAMA}
    else:
        raise Exception("Field nama unit kerja tidak ditemukan. Cek model UnitKerja.")

    set_if_exists(data, UnitKerja, "kode_unit", "REHSOS")
    set_if_exists(data, UnitKerja, "kode", "REHSOS")
    set_if_exists(data, UnitKerja, "alamat", "Jl. Salemba Raya No. 28, Jakarta Pusat")

    unit, created = UnitKerja.objects.get_or_create(**lookup, defaults=data)
    return unit


def random_date(start_year=2020, end_year=2026):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


@transaction.atomic
def run():
    unit = get_or_create_unit_kerja()

    print(f"Unit kerja digunakan: {UNIT_KERJA_NAMA}")

    pegawai_list = []

    # =========================
    # DUMMY MASTER PEGAWAI
    # =========================
    for i in range(1, JUMLAH_DATA + 1):
        nip = f"198{random.randint(0,9)}{random.randint(10,12):02d}{random.randint(10,28):02d}20{random.randint(10,24):02d}1{i:04d}"

        data = {}

        set_if_exists(data, Pegawai, "nip", nip)
        set_if_exists(data, Pegawai, "nama", f"Pegawai Rehabilitasi Sosial {i:02d}")
        set_if_exists(data, Pegawai, "nama_pegawai", f"Pegawai Rehabilitasi Sosial {i:02d}")
        set_if_exists(data, Pegawai, "jabatan", random.choice([
            "Analis Barang Milik Negara",
            "Pengelola Barang Milik Negara",
            "Pranata Komputer Ahli Pertama",
            "Analis Kebijakan Ahli Muda",
            "Pengadministrasi Umum",
            "Penyusun Bahan Laporan",
            "Arsiparis Ahli Pertama",
            "Perencana Ahli Muda",
        ]))
        set_if_exists(data, Pegawai, "pangkat", random.choice([
            "Penata Muda / III-a",
            "Penata Muda Tk. I / III-b",
            "Penata / III-c",
            "Penata Tk. I / III-d",
            "Pembina / IV-a",
        ]))
        set_if_exists(data, Pegawai, "golongan", random.choice([
            "III/a", "III/b", "III/c", "III/d", "IV/a"
        ]))
        set_if_exists(data, Pegawai, "email", f"pegawai.rehsos{i:02d}@kemsos.go.id")
        set_if_exists(data, Pegawai, "no_hp", f"0812{random.randint(10000000,99999999)}")
        set_if_exists(data, Pegawai, "alamat", "Jakarta Pusat")
        set_if_exists(data, Pegawai, "status", "Aktif")
        set_if_exists(data, Pegawai, "unit_kerja", unit)

        lookup = {"nip": nip} if has_field(Pegawai, "nip") else {"nama": f"Pegawai Rehabilitasi Sosial {i:02d}"}

        obj, created = Pegawai.objects.update_or_create(
            **lookup,
            defaults=data
        )
        pegawai_list.append(obj)

    print(f"Berhasil membuat/update {JUMLAH_DATA} data pegawai.")

    # =========================
    # DUMMY MASTER KENDARAAN
    # =========================
    merek_list = ["Toyota", "Honda", "Mitsubishi", "Daihatsu", "Suzuki", "Nissan"]
    tipe_list = ["Avanza", "Innova", "Fortuner", "Xpander", "Terios", "Ertiga", "Livina"]
    warna_list = ["Hitam", "Putih", "Silver", "Abu-abu", "Merah"]
    jenis_list = ["Operasional", "Dinas Jabatan", "Kendaraan Sewa"]

    for i in range(1, JUMLAH_DATA + 1):
        nomor_polisi = f"B {1000+i} KRS"

        data = {}

        set_if_exists(data, Kendaraan, "kode_kendaraan", f"KDR-REHSOS-{i:03d}")
        set_if_exists(data, Kendaraan, "nomor_polisi", nomor_polisi)
        set_if_exists(data, Kendaraan, "merek", random.choice(merek_list))
        set_if_exists(data, Kendaraan, "tipe", random.choice(tipe_list))
        set_if_exists(data, Kendaraan, "jenis_kendaraan", random.choice(jenis_list))
        set_if_exists(data, Kendaraan, "tahun_pembuatan", random.randint(2016, 2025))
        set_if_exists(data, Kendaraan, "tahun_perolehan", random.randint(2017, 2026))
        set_if_exists(data, Kendaraan, "warna", random.choice(warna_list))
        set_if_exists(data, Kendaraan, "nomor_rangka", f"RANGKAREHSOS{i:08d}")
        set_if_exists(data, Kendaraan, "nomor_mesin", f"MESINREHSOS{i:08d}")
        set_if_exists(data, Kendaraan, "nomor_bpkb", f"BPKB-REHSOS-{i:05d}")
        set_if_exists(data, Kendaraan, "nomor_stnk", f"STNK-REHSOS-{i:05d}")
        set_if_exists(data, Kendaraan, "masa_berlaku_stnk", date.today() + timedelta(days=random.randint(90, 900)))
        set_if_exists(data, Kendaraan, "jatuh_tempo_pajak", date.today() + timedelta(days=random.randint(60, 365)))
        set_if_exists(data, Kendaraan, "nup", f"{i:03d}")
        set_if_exists(data, Kendaraan, "kode_barang", "3.02.01.02.003")
        set_if_exists(data, Kendaraan, "nilai_perolehan", random.randint(150000000, 600000000))
        set_if_exists(data, Kendaraan, "kondisi", random.choice(["Baik", "Rusak Ringan", "Rusak Berat"]))
        set_if_exists(data, Kendaraan, "status_pemanfaatan", random.choice([
            "Digunakan",
            "Idle",
            "Dikuasai pihak lain",
            "Tidak diketahui keberadaannya",
        ]))
        set_if_exists(data, Kendaraan, "kilometer_terakhir", random.randint(5000, 180000))
        set_if_exists(data, Kendaraan, "unit_kerja", unit)

        # Pengguna kendaraan sengaja tidak diisi karena pengguna hanya pada SIP Kendaraan.
        # Kalau model masih punya field pengguna, dibiarkan kosong.

        lookup = {"nomor_polisi": nomor_polisi} if has_field(Kendaraan, "nomor_polisi") else {"kode_kendaraan": f"KDR-REHSOS-{i:03d}"}

        Kendaraan.objects.update_or_create(
            **lookup,
            defaults=data
        )

    print(f"Berhasil membuat/update {JUMLAH_DATA} data kendaraan.")

    # =========================
    # DUMMY MASTER RUMAH NEGARA
    # =========================
    kecamatan_list = ["Senen", "Matraman", "Cempaka Putih", "Johar Baru", "Menteng"]
    kondisi_list = ["Baik", "Rusak Ringan", "Rusak Berat"]
    status_list = ["Dihuni", "Kosong", "Dalam penguasaan pihak lain"]

    for i in range(1, JUMLAH_DATA + 1):
        kode_rumah = f"RN-REHSOS-{i:03d}"

        data = {}

        set_if_exists(data, Rumah, "kode_rumah", kode_rumah)
        set_if_exists(data, Rumah, "kode_rumah_negara", kode_rumah)
        set_if_exists(data, Rumah, "nama_rumah", f"Rumah Negara Rehsos {i:02d}")
        set_if_exists(data, Rumah, "alamat", f"Jl. Rehabilitasi Sosial No. {i}, Jakarta")
        set_if_exists(data, Rumah, "kelurahan", f"Kelurahan Dummy {i:02d}")
        set_if_exists(data, Rumah, "kecamatan", random.choice(kecamatan_list))
        set_if_exists(data, Rumah, "kota", "Jakarta Pusat")
        set_if_exists(data, Rumah, "provinsi", "DKI Jakarta")
        set_if_exists(data, Rumah, "luas_tanah", random.randint(80, 300))
        set_if_exists(data, Rumah, "luas_bangunan", random.randint(45, 180))
        set_if_exists(data, Rumah, "tahun_perolehan", random.randint(1990, 2025))
        set_if_exists(data, Rumah, "nup", f"{i:03d}")
        set_if_exists(data, Rumah, "kode_barang", "4.01.01.01.001")
        set_if_exists(data, Rumah, "nilai_perolehan", random.randint(300000000, 2500000000))
        set_if_exists(data, Rumah, "kondisi", random.choice(kondisi_list))
        set_if_exists(data, Rumah, "status_penghunian", random.choice(status_list))
        set_if_exists(data, Rumah, "status", random.choice(status_list))
        set_if_exists(data, Rumah, "keterangan", "Data dummy untuk pengujian aplikasi SIKARIS")
        set_if_exists(data, Rumah, "latitude", -6.175392 + random.uniform(-0.05, 0.05))
        set_if_exists(data, Rumah, "longitude", 106.827153 + random.uniform(-0.05, 0.05))
        set_if_exists(data, Rumah, "unit_kerja", unit)

        if has_field(Rumah, "penghuni") and pegawai_list:
            data["penghuni"] = random.choice(pegawai_list)

        if has_field(Rumah, "pemakai") and pegawai_list:
            data["pemakai"] = random.choice(pegawai_list)

        lookup = {}

        if has_field(Rumah, "kode_rumah"):
            lookup = {"kode_rumah": kode_rumah}
        elif has_field(Rumah, "kode_rumah_negara"):
            lookup = {"kode_rumah_negara": kode_rumah}
        else:
            lookup = {"nama_rumah": f"Rumah Negara Rehsos {i:02d}"}

        Rumah.objects.update_or_create(
            **lookup,
            defaults=data
        )

    print(f"Berhasil membuat/update {JUMLAH_DATA} data rumah negara.")
    print("SELESAI: Data dummy berhasil dibuat.")


run()