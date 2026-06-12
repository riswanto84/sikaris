from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from master.models import UnitKerja, Pegawai, Kendaraan, RumahDinas
from kendaraan.models import SIPKendaraan, ServiceKendaraan, RiwayatKondisiKendaraan
from rumah_dinas.models import SIPRumahDinas


class Command(BaseCommand):
    help = (
        "Generate 100 data dummy untuk Pegawai, Kendaraan, Rumah Negara, "
        "SIP Kendaraan, SIP Rumah Negara, Service Kendaraan, dan Riwayat Kondisi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--jumlah",
            type=int,
            default=100,
            help="Jumlah data dummy per tabel utama. Default: 100.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Hapus data dummy lama dengan prefix DMY sebelum generate ulang.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        jumlah = options["jumlah"]
        if jumlah < 1:
            self.stderr.write(self.style.ERROR("Jumlah minimal 1."))
            return

        if options["clear"]:
            self._clear_dummy_data()
            self.stdout.write(self.style.WARNING("Data dummy lama berhasil dihapus."))

        today = date.today()
        unit_list = self._create_unit_kerja()
        pegawai_list = self._create_pegawai(jumlah, unit_list)
        kendaraan_list = self._create_kendaraan(jumlah, unit_list, pegawai_list, today)
        rumah_list = self._create_rumah_dinas(jumlah, pegawai_list, today)
        self._create_sip_kendaraan(jumlah, kendaraan_list, pegawai_list, today)
        self._create_sip_rumah_dinas(jumlah, rumah_list, pegawai_list, today)
        self._create_service_kendaraan(jumlah, kendaraan_list, today)
        self._create_riwayat_kondisi(jumlah, kendaraan_list, today)

        self.stdout.write(self.style.SUCCESS("Selesai generate data dummy."))
        self.stdout.write(self.style.SUCCESS(f"Pegawai: {jumlah}"))
        self.stdout.write(self.style.SUCCESS(f"Kendaraan: {jumlah}"))
        self.stdout.write(self.style.SUCCESS(f"Rumah Negara: {jumlah}"))
        self.stdout.write(self.style.SUCCESS(f"SIP Kendaraan: {jumlah}"))
        self.stdout.write(self.style.SUCCESS(f"SIP Rumah Negara: {jumlah}"))
        self.stdout.write(self.style.SUCCESS(f"Service Kendaraan: {jumlah}"))
        self.stdout.write(self.style.SUCCESS(f"Riwayat Kondisi Kendaraan: {jumlah}"))

    def _clear_dummy_data(self):
        RiwayatKondisiKendaraan.objects.filter(kendaraan__kode_kendaraan__startswith="DMY-KDR-").delete()
        ServiceKendaraan.objects.filter(kendaraan__kode_kendaraan__startswith="DMY-KDR-").delete()
        SIPKendaraan.objects.filter(nomor_sip__startswith="DMY-SIP-KDR-").delete()
        SIPRumahDinas.objects.filter(nomor_sip__startswith="DMY-SIP-RD-").delete()
        Kendaraan.objects.filter(kode_kendaraan__startswith="DMY-KDR-").delete()
        RumahDinas.objects.filter(kode_rumah__startswith="DMY-RD-").delete()
        Pegawai.objects.filter(nip__startswith="DMY").delete()
        UnitKerja.objects.filter(nama_unit__startswith="Dummy Unit Kerja").delete()

    def _create_unit_kerja(self):
        unit_names = [
            "Dummy Unit Kerja Biro Umum",
            "Dummy Unit Kerja Keuangan",
            "Dummy Unit Kerja Kepegawaian",
            "Dummy Unit Kerja Perencanaan",
            "Dummy Unit Kerja BMN",
            "Dummy Unit Kerja Logistik",
            "Dummy Unit Kerja Pusdatin",
            "Dummy Unit Kerja Rehabilitasi Sosial",
            "Dummy Unit Kerja Perlindungan Sosial",
            "Dummy Unit Kerja Pendidikan dan Pelatihan",
        ]
        result = []
        for name in unit_names:
            unit, _ = UnitKerja.objects.update_or_create(
                nama_unit=name,
                defaults={"keterangan": "Data dummy untuk kebutuhan uji coba aplikasi SIKARIS."},
            )
            result.append(unit)
        return result

    def _create_pegawai(self, jumlah, unit_list):
        jabatan_list = [
            "Analis BMN", "Pengelola Kendaraan", "Pengelola Rumah Negara",
            "Pranata Komputer", "Arsiparis", "Bendahara", "Verifikator",
            "Pengadministrasi Umum", "Kepala Subbagian", "Staf Operasional",
        ]
        pangkat_list = ["Penata Muda", "Penata", "Penata Tk. I", "Pembina", "Pembina Tk. I"]
        golongan_list = ["III/a", "III/b", "III/c", "III/d", "IV/a"]
        result = []
        for i in range(1, jumlah + 1):
            pegawai, _ = Pegawai.objects.update_or_create(
                nip=f"DMY{202600000000000000 + i}",
                defaults={
                    "nik": f"3275{str(i).zfill(12)}",
                    "nama": f"Pegawai Dummy {str(i).zfill(3)}",
                    "jabatan": jabatan_list[(i - 1) % len(jabatan_list)],
                    "pangkat": pangkat_list[(i - 1) % len(pangkat_list)],
                    "golongan": golongan_list[(i - 1) % len(golongan_list)],
                    "unit_kerja": unit_list[(i - 1) % len(unit_list)],
                    "no_hp": f"0812{str(70000000 + i).zfill(8)}",
                    "email": f"pegawai.dummy{i:03d}@example.com",
                    "alamat": f"Jl. Dummy Pegawai Nomor {i}, Bekasi",
                    "status_pegawai": "Aktif",
                },
            )
            result.append(pegawai)
        return result

    def _create_kendaraan(self, jumlah, unit_list, pegawai_list, today):
        # jenis_kendaraan sekarang dibuat bervariasi agar data dummy mewakili
        # mobil, sepeda motor, motor roda 3, dan kendaraan lainnya.
        kendaraan_template = [
            {"jenis": "MOBIL", "merek": "Toyota", "tipe": "Avanza", "kode_barang": "3.02.01.02.003", "nilai_awal": 150_000_000, "km_awal": 10_000},
            {"jenis": "MOBIL", "merek": "Toyota", "tipe": "Innova", "kode_barang": "3.02.01.02.003", "nilai_awal": 240_000_000, "km_awal": 15_000},
            {"jenis": "MOBIL", "merek": "Mitsubishi", "tipe": "Xpander", "kode_barang": "3.02.01.02.003", "nilai_awal": 210_000_000, "km_awal": 12_000},
            {"jenis": "SEPEDA_MOTOR", "merek": "Honda", "tipe": "Vario 160", "kode_barang": "3.02.01.04.001", "nilai_awal": 28_000_000, "km_awal": 5_000},
            {"jenis": "SEPEDA_MOTOR", "merek": "Yamaha", "tipe": "NMAX", "kode_barang": "3.02.01.04.001", "nilai_awal": 32_000_000, "km_awal": 7_000},
            {"jenis": "SEPEDA_MOTOR", "merek": "Honda", "tipe": "PCX", "kode_barang": "3.02.01.04.001", "nilai_awal": 35_000_000, "km_awal": 6_500},
            {"jenis": "MOTOR_RODA_3", "merek": "Viar", "tipe": "Karya 200", "kode_barang": "3.02.01.04.002", "nilai_awal": 38_000_000, "km_awal": 4_500},
            {"jenis": "MOTOR_RODA_3", "merek": "Nozomi", "tipe": "Azabu 250", "kode_barang": "3.02.01.04.002", "nilai_awal": 42_000_000, "km_awal": 4_000},
            {"jenis": "KENDARAAN_LAINNYA", "merek": "Isuzu", "tipe": "Elf", "kode_barang": "3.02.01.02.004", "nilai_awal": 320_000_000, "km_awal": 20_000},
            {"jenis": "KENDARAAN_LAINNYA", "merek": "Mitsubishi", "tipe": "L300", "kode_barang": "3.02.01.02.004", "nilai_awal": 190_000_000, "km_awal": 18_000},
        ]
        warna_list = ["Hitam", "Putih", "Silver", "Abu-Abu", "Biru", "Merah"]
        kondisi_list = ["BAIK", "BAIK", "BAIK", "RUSAK_RINGAN", "RUSAK_BERAT"]
        result = []
        for i in range(1, jumlah + 1):
            template = kendaraan_template[(i - 1) % len(kendaraan_template)]
            kendaraan, _ = Kendaraan.objects.update_or_create(
                kode_kendaraan=f"DMY-KDR-{i:03d}",
                defaults={
                    "nomor_polisi": f"B {9000 + i} DMY",
                    "merek": template["merek"],
                    "tipe": template["tipe"],
                    "jenis_kendaraan": template["jenis"],
                    "tahun_pembuatan": 2016 + (i % 9),
                    "tahun_perolehan": 2017 + (i % 8),
                    "warna": warna_list[(i - 1) % len(warna_list)],
                    "nomor_rangka": f"RANGKA-DMY-{i:06d}",
                    "nomor_mesin": f"MESIN-DMY-{i:06d}",
                    "nomor_bpkb": f"BPKB-DMY-{i:06d}",
                    "nomor_stnk": f"STNK-DMY-{i:06d}",
                    "masa_berlaku_stnk": today + timedelta(days=180 + i),
                    "jatuh_tempo_pajak": today + timedelta(days=90 + i),
                    "nup": f"NUP-KDR-{i:04d}",
                    "kode_barang": template["kode_barang"],
                    "nilai_perolehan": Decimal(template["nilai_awal"] + (i * 2_500_000)),
                    "unit_kerja": unit_list[(i - 1) % len(unit_list)],
                    "pengguna": pegawai_list[(i - 1) % len(pegawai_list)] if i % 5 != 0 else None,
                    "kondisi": kondisi_list[(i - 1) % len(kondisi_list)],
                    "status_pemanfaatan": "DIGUNAKAN" if i % 5 != 0 else "TERSEDIA",
                    "kilometer_terakhir": template["km_awal"] + (i * 750),
                },
            )
            result.append(kendaraan)
        return result

    def _create_rumah_dinas(self, jumlah, pegawai_list, today):
        kondisi_list = ["BAIK", "BAIK", "RUSAK_RINGAN", "BAIK", "RUSAK_BERAT"]
        result = []
        for i in range(1, jumlah + 1):
            rumah, _ = RumahDinas.objects.update_or_create(
                kode_rumah=f"DMY-RD-{i:03d}",
                defaults={
                    "nama_rumah": f"Rumah Negara Dummy {i:03d}",
                    "jenis_rumah": "Rumah Negara Golongan II" if i % 2 == 0 else "Rumah Negara Golongan I",
                    "alamat": f"Komplek Rumah Negara Dummy Blok {chr(65 + ((i - 1) % 26))} No. {i}, Jakarta",
                    "provinsi": "DKI Jakarta",
                    "kabupaten_kota": "Jakarta Pusat",
                    "kecamatan": "Gambir",
                    "kelurahan": "Petojo Selatan",
                    "latitude": Decimal("-6.17511000") + Decimal(i) / Decimal("100000"),
                    "longitude": Decimal("106.86503900") + Decimal(i) / Decimal("100000"),
                    "luas_tanah": Decimal(90 + (i % 40)),
                    "luas_bangunan": Decimal(45 + (i % 25)),
                    "jumlah_kamar_tidur": 2 + (i % 3),
                    "jumlah_kamar_mandi": 1 + (i % 2),
                    "daya_listrik": "2200 VA" if i % 2 == 0 else "1300 VA",
                    "tahun_dibangun": 2000 + (i % 20),
                    "tahun_perolehan": 2001 + (i % 19),
                    "nup": f"NUP-RD-{i:04d}",
                    "kode_barang": "3.01.01.01.001",
                    "nilai_perolehan": Decimal(350_000_000 + (i * 7_500_000)),
                    "unit_kerja": pegawai_list[(i - 1) % len(pegawai_list)].unit_kerja,
                    "nomor_sertifikat": f"SERT-DMY-{i:06d}",
                    "status_tanah": "Milik Negara",
                    "kondisi": kondisi_list[(i - 1) % len(kondisi_list)],
                    "status_pemanfaatan": "DIHUNI" if i % 4 != 0 else "KOSONG",
                },
            )
            result.append(rumah)
        return result

    def _create_sip_kendaraan(self, jumlah, kendaraan_list, pegawai_list, today):
        status_list = ["AKTIF", "BERAKHIR", "DICABUT", "DISETUJUI"]
        for i in range(1, jumlah + 1):
            mulai = today - timedelta(days=365 - i)
            akhir = mulai + timedelta(days=180 + (i % 180))
            kendaraan = kendaraan_list[(i - 1) % len(kendaraan_list)]
            pegawai = pegawai_list[(i + 7) % len(pegawai_list)]
            SIPKendaraan.objects.update_or_create(
                nomor_sip=f"DMY-SIP-KDR-{i:03d}",
                defaults={
                    "tanggal_sip": mulai - timedelta(days=7),
                    "kendaraan": kendaraan,
                    "pegawai": pegawai,
                    "tanggal_mulai": mulai,
                    "tanggal_akhir": akhir,
                    "jenis_pemakaian": kendaraan.jenis_kendaraan or "MOBIL",
                    "tujuan_pemakaian": "Data dummy penggunaan kendaraan dinas untuk uji coba laporan dan export.",
                    "lokasi_penggunaan": "Jakarta dan sekitarnya",
                    "dasar_penerbitan": "Surat tugas dummy dan kebutuhan operasional unit kerja.",
                    "pejabat_penandatangan": "Pejabat Penandatangan Dummy",
                    "status": status_list[(i - 1) % len(status_list)],
                    "catatan": "Data dummy SIP kendaraan.",
                },
            )

    def _create_sip_rumah_dinas(self, jumlah, rumah_list, pegawai_list, today):
        status_list = ["AKTIF", "BERAKHIR", "PENGOSONGAN", "DISETUJUI"]
        for i in range(1, jumlah + 1):
            mulai = today - timedelta(days=730 - (i * 3))
            akhir = mulai + timedelta(days=365 + (i % 365))
            SIPRumahDinas.objects.update_or_create(
                nomor_sip=f"DMY-SIP-RD-{i:03d}",
                defaults={
                    "tanggal_sip": mulai - timedelta(days=14),
                    "rumah_dinas": rumah_list[(i - 1) % len(rumah_list)],
                    "pegawai": pegawai_list[(i + 13) % len(pegawai_list)],
                    "penghuni": pegawai_list[(i + 17) % len(pegawai_list)] if i % 3 == 0 else pegawai_list[(i + 13) % len(pegawai_list)],
                    "tanggal_mulai": mulai,
                    "tanggal_akhir": akhir,
                    "dasar_penerbitan": "Keputusan penggunaan rumah negara dummy.",
                    "pejabat_penandatangan": "Pejabat Penandatangan Dummy",
                    "jumlah_anggota_keluarga": i % 6,
                    "status": status_list[(i - 1) % len(status_list)],
                    "status_bayar_pnbp": "SUDAH_BAYAR" if i % 2 == 0 else "BELUM_BAYAR",
                    "tahun_pnbp": today.year,
                    "nilai_pnbp": Decimal(1500000 + (i * 25000)),
                    "tanggal_bayar_pnbp": today - timedelta(days=i) if i % 2 == 0 else None,
                    "catatan": "Data dummy SIP rumah negara. Penghuni aktual dapat berbeda dengan pemegang SIP.",
                },
            )

    def _create_service_kendaraan(self, jumlah, kendaraan_list, today):
        jenis_service_list = [
            "SERVICE_BERKALA", "GANTI_OLI", "GANTI_BAN", "GANTI_AKI",
            "PERBAIKAN_MESIN", "PERBAIKAN_BODY", "LAINNYA",
        ]
        kondisi_list = ["BAIK", "RUSAK_RINGAN", "RUSAK_BERAT"]
        for i in range(1, jumlah + 1):
            biaya_jasa = Decimal(150_000 + (i * 5_000))
            biaya_sparepart = Decimal(250_000 + (i * 10_000))
            ServiceKendaraan.objects.update_or_create(
                kendaraan=kendaraan_list[(i - 1) % len(kendaraan_list)],
                tanggal_service=today - timedelta(days=i * 2),
                jenis_service=jenis_service_list[(i - 1) % len(jenis_service_list)],
                defaults={
                    "kilometer": 10_000 + (i * 800),
                    "bengkel": f"Bengkel Rekanan Dummy {((i - 1) % 10) + 1}",
                    "uraian_pekerjaan": f"Pekerjaan service dummy nomor {i}: pengecekan umum, penggantian part, dan test drive.",
                    "sparepart_diganti": "Oli mesin, filter oli, kampas rem" if i % 2 == 0 else "Tidak ada sparepart besar",
                    "biaya_jasa": biaya_jasa,
                    "biaya_sparepart": biaya_sparepart,
                    "total_biaya": biaya_jasa + biaya_sparepart,
                    "kondisi_sebelum": kondisi_list[i % len(kondisi_list)],
                    "kondisi_sesudah": "BAIK" if i % 4 != 0 else "RUSAK_RINGAN",
                },
            )

    def _create_riwayat_kondisi(self, jumlah, kendaraan_list, today):
        kondisi_list = ["BAIK", "RUSAK_RINGAN", "BAIK", "RUSAK_BERAT", "BAIK"]
        for i in range(1, jumlah + 1):
            RiwayatKondisiKendaraan.objects.update_or_create(
                kendaraan=kendaraan_list[(i - 1) % len(kendaraan_list)],
                tanggal=today - timedelta(days=i),
                defaults={
                    "kondisi": kondisi_list[(i - 1) % len(kondisi_list)],
                    "uraian_kondisi": f"Catatan kondisi dummy nomor {i}. Pemeriksaan visual dan kelengkapan kendaraan.",
                },
            )
