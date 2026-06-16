import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from master.models import UnitKerja, Pegawai, Kendaraan, RumahDinas
from kendaraan.models import SIPKendaraan, ServiceKendaraan, RiwayatKondisiKendaraan
from rumah_dinas.models import SIPRumahDinas, PerbaikanRumahDinas
from penghapusan.models import PermohonanPenghapusanBMN, BarangPenghapusanBMN
from psp.models import PermohonanPSPBMN, BarangPSP

try:
    from tanah_negara.models import TanahNegara
except Exception:  # pragma: no cover
    TanahNegara = None


SATKER_SAMPLE = [
    ("Sekretariat Jenderal", "BIRO_UMUM"),
    ("Biro Umum", "BIRO_UMUM"),
    ("Biro Keuangan", "LAINNYA"),
    ("Pusat Data dan Informasi Kesejahteraan Sosial", "PUSAT"),
    ("Pusat Pendidikan, Pelatihan, dan Pengembangan Profesi Kesejahteraan Sosial", "PUSAT"),
    ("Sekretariat Direktorat Jenderal Rehabilitasi Sosial", "DITJEN"),
    ("Sekretariat Direktorat Jenderal Perlindungan dan Jaminan Sosial", "DITJEN"),
    ("Sekretariat Direktorat Jenderal Pemberdayaan Sosial", "DITJEN"),
    ("Sekretariat Inspektorat Jenderal", "ITJEN"),
    ("Sentra Handayani Jakarta", "SENTRA"),
    ("Sentra Mulya Jaya Jakarta", "SENTRA"),
    ("Sentra Terpadu Pangudi Luhur Bekasi", "SENTRA"),
    ("Balai Besar Pendidikan dan Pelatihan Kesejahteraan Sosial Bandung", "BALAI"),
    ("Balai Besar Pendidikan dan Pelatihan Kesejahteraan Sosial Yogyakarta", "BALAI"),
    ("Balai Besar Pendidikan dan Pelatihan Kesejahteraan Sosial Makassar", "BALAI"),
]

NAMA_DEPAN = ["Ahmad", "Budi", "Citra", "Dewi", "Eka", "Fajar", "Gita", "Hendra", "Indah", "Joko", "Kartika", "Lukman", "Maya", "Nugroho", "Putri", "Rizky", "Sari", "Teguh", "Utami", "Wahyu"]
NAMA_BELAKANG = ["Pratama", "Saputra", "Wijaya", "Santoso", "Wibowo", "Kusuma", "Lestari", "Nugraha", "Permana", "Maulana", "Hidayat", "Firmansyah"]
MEREK = ["Toyota", "Daihatsu", "Honda", "Suzuki", "Mitsubishi", "Nissan", "Yamaha", "Honda Motor", "Kawasaki"]
TIPE = ["Avanza", "Innova", "Brio", "Ertiga", "Xpander", "Terios", "Vario", "NMAX", "Beat", "Hilux"]
KOTA = ["Jakarta", "Bekasi", "Bogor", "Tangerang", "Bandung", "Yogyakarta", "Semarang", "Surabaya", "Makassar", "Medan"]


def rand_date(days_back=730, days_forward=120):
    today = timezone.now().date()
    return today + timedelta(days=random.randint(-days_back, days_forward))


def add_days(d, min_days=30, max_days=365):
    return d + timedelta(days=random.randint(min_days, max_days))


def money(min_value, max_value, step=100000):
    value = random.randrange(int(min_value), int(max_value), step)
    return Decimal(value)


def choice_value(choices):
    return random.choice([x[0] for x in choices])


class Command(BaseCommand):
    help = "Membuat seed data random untuk seluruh transaksi SIKARIS pada berbagai satker. Default 300 data per jenis transaksi."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=300, help="Jumlah data per jenis transaksi. Default: 300")
        parser.add_argument("--clear", action="store_true", help="Hapus data transaksi dummy lama sebelum membuat data baru")
        parser.add_argument("--seed", type=int, default=20260616, help="Seed random agar hasil konsisten")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        count = options["count"]
        user = self._get_or_create_user()

        if options["clear"]:
            self._clear_dummy_transactions()

        units = self._ensure_units()
        pegawai = self._ensure_pegawai(units, max(count + 80, 380))
        kendaraan = self._ensure_kendaraan(units, pegawai, max(count + 60, 360))
        rumah = self._ensure_rumah(units, max(count + 60, 360))

        created = {}
        created["SIP Kendaraan"] = self._seed_sip_kendaraan(count, kendaraan, pegawai, user)
        created["Service Kendaraan"] = self._seed_service_kendaraan(count, kendaraan, user)
        created["Riwayat Kondisi Kendaraan"] = self._seed_riwayat_kondisi(count, kendaraan, user)
        created["SIP Rumah Negara"] = self._seed_sip_rumah(count, rumah, pegawai, user)
        created["Perbaikan Rumah Negara"] = self._seed_perbaikan_rumah(count, rumah, pegawai)
        created["Permohonan Penghapusan BMN"] = self._seed_penghapusan(count, units, pegawai, kendaraan, rumah, user)
        created["Permohonan PSP BMN"] = self._seed_psp(count, units, pegawai, kendaraan, rumah, user)

        self.stdout.write(self.style.SUCCESS("Seed data transaksi SIKARIS selesai."))
        for label, total in created.items():
            self.stdout.write(f"- {label}: {total} data")
        self.stdout.write("\nCara pakai ulang:")
        self.stdout.write("  python manage.py seed_transaksi_random --count 300")
        self.stdout.write("  python manage.py seed_transaksi_random --count 300 --clear")

    def _get_or_create_user(self):
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if user:
            return user
        return User.objects.create_user(username="admin", password="admin12345", email="admin@sikaris.local", is_staff=True, is_superuser=True)

    def _clear_dummy_transactions(self):
        prefixes = ["DUMMY", "SIMULASI", "UP-BMN", "PSP"]
        BarangPSP.objects.filter(permohonan__catatan_unit__icontains="DUMMY-SEED-SIKARIS").delete()
        BarangPenghapusanBMN.objects.filter(permohonan__catatan_unit__icontains="DUMMY-SEED-SIKARIS").delete()
        PermohonanPSPBMN.objects.filter(catatan_unit__icontains="DUMMY-SEED-SIKARIS").delete()
        PermohonanPenghapusanBMN.objects.filter(catatan_unit__icontains="DUMMY-SEED-SIKARIS").delete()
        PerbaikanRumahDinas.objects.filter(uraian_kerusakan__icontains="DUMMY-SEED-SIKARIS").delete()
        SIPRumahDinas.objects.filter(catatan__icontains="DUMMY-SEED-SIKARIS").delete()
        RiwayatKondisiKendaraan.objects.filter(uraian_kondisi__icontains="DUMMY-SEED-SIKARIS").delete()
        ServiceKendaraan.objects.filter(uraian_pekerjaan__icontains="DUMMY-SEED-SIKARIS").delete()
        SIPKendaraan.objects.filter(catatan__icontains="DUMMY-SEED-SIKARIS").delete()

    def _ensure_units(self):
        units = []
        for nama, jenis in SATKER_SAMPLE:
            obj, _ = UnitKerja.objects.get_or_create(nama_unit=nama, defaults={"jenis_unit": jenis, "keterangan": "DUMMY-SEED-SIKARIS"})
            if not obj.jenis_unit:
                obj.jenis_unit = jenis
                obj.save(update_fields=["jenis_unit", "updated_at"])
            units.append(obj)
        return units

    def _ensure_pegawai(self, units, minimum):
        existing = list(Pegawai.objects.all())
        need = max(0, minimum - len(existing))
        jabatan_list = ["Analis BMN", "Pengelola Kendaraan", "Pengadministrasi Umum", "Kepala Subbagian Tata Usaha", "Pranata Keuangan", "Arsiparis", "Pengelola Rumah Negara"]
        for i in range(need):
            nama = f"{random.choice(NAMA_DEPAN)} {random.choice(NAMA_BELAKANG)} {i+1:03d}"
            nip = f"198{random.randint(0,9)}{random.randint(1,12):02d}{random.randint(1,28):02d}20{random.randint(10,24):02d}{random.randint(1,999999):06d}"[:18]
            while Pegawai.objects.filter(nip=nip).exists():
                nip = str(random.randint(197001010000000000, 199912319999999999))[:18]
            Pegawai.objects.create(
                nip=nip,
                nik=str(random.randint(3171000000000000, 3276999999999999)),
                nama=nama,
                jabatan=random.choice(jabatan_list),
                pangkat=random.choice(["Penata", "Penata Tk. I", "Pembina", "Pengatur"]),
                golongan=random.choice(["II/c", "II/d", "III/a", "III/b", "III/c", "III/d", "IV/a"]),
                unit_kerja=random.choice(units),
                no_hp=f"08{random.randint(1000000000, 9999999999)}",
                email=f"pegawai{i+1:03d}@sikaris.local",
                alamat=f"Jl. Simulasi No. {random.randint(1,200)}, {random.choice(KOTA)}",
                status_pegawai="Aktif",
            )
        return list(Pegawai.objects.all())

    def _ensure_kendaraan(self, units, pegawai, minimum):
        existing = list(Kendaraan.objects.all())
        need = max(0, minimum - len(existing))
        jenis_choices = ["MOBIL", "SEPEDA_MOTOR", "MOTOR_RODA_3", "OPERASIONAL", "DINAS_JABATAN", "KENDARAAN_SEWA"]
        for i in range(need):
            kode = f"DUMMY-KDR-{i+1:05d}"
            while Kendaraan.objects.filter(kode_kendaraan=kode).exists():
                kode = f"DUMMY-KDR-{random.randint(1,999999):06d}"
            nopol = f"B {random.randint(1000,9999)} {random.choice(['ABC','BME','KMS','SRS','PDS','REH'])}"
            while Kendaraan.objects.filter(nomor_polisi=nopol).exists():
                nopol = f"B {random.randint(1000,9999)} {random.choice(['AA','BB','CC','DD','EE'])}"
            unit = random.choice(units)
            Kendaraan.objects.create(
                kode_kendaraan=kode,
                nomor_polisi=nopol,
                merek=random.choice(MEREK),
                tipe=random.choice(TIPE),
                jenis_kendaraan=random.choice(jenis_choices),
                tahun_pembuatan=random.randint(2012, 2025),
                tahun_perolehan=random.randint(2012, 2025),
                warna=random.choice(["Hitam", "Putih", "Silver", "Abu-abu", "Merah"]),
                nomor_rangka=f"RNG{random.randint(1000000000,9999999999)}",
                nomor_mesin=f"MSN{random.randint(1000000000,9999999999)}",
                nomor_bpkb=f"BPKB-{random.randint(100000,999999)}",
                nomor_stnk=f"STNK-{random.randint(100000,999999)}",
                masa_berlaku_stnk=add_days(timezone.now().date(), 30, 900),
                jatuh_tempo_pajak=add_days(timezone.now().date(), 30, 365),
                nup=str(random.randint(1, 999)),
                kode_barang=f"3.02.01.{random.randint(1,99):02d}.{random.randint(1,999):03d}",
                nilai_perolehan=money(25000000, 550000000),
                unit_kerja=unit,
                pengguna=random.choice([p for p in pegawai if p.unit_kerja_id == unit.id] or pegawai),
                kondisi=random.choice(["BAIK", "BAIK", "RUSAK_RINGAN", "RUSAK_BERAT"]),
                status_pemanfaatan=random.choice(["TERSEDIA", "DIGUNAKAN", "DALAM_SERVICE", "TIDAK_AKTIF", "TIDAK_DIKETAHUI", "DIKUASAI_PIHAK_LAIN"]),
                kilometer_terakhir=random.randint(1000, 180000),
            )
        return list(Kendaraan.objects.all())

    def _ensure_rumah(self, units, minimum):
        existing = list(RumahDinas.objects.all())
        need = max(0, minimum - len(existing))
        for i in range(need):
            kode = f"DUMMY-RN-{i+1:05d}"
            while RumahDinas.objects.filter(kode_rumah=kode).exists():
                kode = f"DUMMY-RN-{random.randint(1,999999):06d}"
            kota = random.choice(KOTA)
            RumahDinas.objects.create(
                kode_rumah=kode,
                nama_rumah=f"Rumah Negara Simulasi {i+1:03d}",
                jenis_rumah=random.choice(["Rumah Negara Golongan I", "Rumah Negara Golongan II", "Rumah Negara Golongan III"]),
                alamat=f"Kompleks Rumah Negara Blok {random.choice(['A','B','C','D'])} No. {random.randint(1,200)}, {kota}",
                provinsi=random.choice(["DKI Jakarta", "Jawa Barat", "Banten", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur"]),
                kabupaten_kota=kota,
                kecamatan="Kecamatan Simulasi",
                kelurahan="Kelurahan Simulasi",
                latitude=Decimal(str(round(random.uniform(-6.9, -5.8), 8))),
                longitude=Decimal(str(round(random.uniform(106.3, 107.3), 8))),
                luas_tanah=Decimal(random.randint(90, 600)),
                luas_bangunan=Decimal(random.randint(36, 220)),
                jumlah_kamar_tidur=random.randint(1, 5),
                jumlah_kamar_mandi=random.randint(1, 3),
                daya_listrik=random.choice(["1300 VA", "2200 VA", "3500 VA", "4400 VA"]),
                tahun_dibangun=random.randint(1985, 2020),
                tahun_perolehan=random.randint(1985, 2020),
                nup=str(random.randint(1, 999)),
                kode_barang=f"3.01.01.{random.randint(1,99):02d}.{random.randint(1,999):03d}",
                nilai_perolehan=money(250000000, 3500000000),
                unit_kerja=random.choice(units),
                nomor_sertifikat=f"SHM/SIKARIS/{random.randint(1000,9999)}",
                status_tanah=random.choice(["Sertifikat Hak Pakai", "Sertifikat Hak Milik Pemerintah", "Dalam Proses Sertifikasi"]),
                kondisi=random.choice(["BAIK", "BAIK", "RUSAK_RINGAN", "RUSAK_BERAT"]),
                status_pemanfaatan=random.choice(["KOSONG", "DIHUNI", "DALAM_PERBAIKAN", "TIDAK_AKTIF", "DALAM_PENGUASAAN_PIHAK_LAIN"]),
            )
        return list(RumahDinas.objects.all())

    def _seed_sip_kendaraan(self, count, kendaraan, pegawai, user):
        statuses = ["DRAFT", "DIAJUKAN", "DISETUJUI", "DITOLAK", "TERBIT", "MENUNGGU_TTE", "BERAKHIR", "DIBATALKAN"]
        total = 0
        for i in range(count):
            k = random.choice(kendaraan)
            p = random.choice([x for x in pegawai if x.unit_kerja_id == k.unit_kerja_id] or pegawai)
            mulai = rand_date(700, 30)
            akhir = add_days(mulai, 30, 365)
            st = random.choice(statuses)
            sip = SIPKendaraan(
                tanggal_sip=mulai,
                kendaraan=k,
                pegawai=p,
                tanggal_mulai=mulai,
                tanggal_akhir=akhir,
                jenis_pemakaian=random.choice(["OPERASIONAL", "DINAS_JABATAN", "KENDARAAN_SEWA", "MOBIL", "SEPEDA_MOTOR"]),
                tujuan_pemakaian="DUMMY-SEED-SIKARIS - pemakaian kendaraan untuk operasional kedinasan.",
                lokasi_penggunaan=random.choice(KOTA),
                dasar_penerbitan="Nota dinas dan kebutuhan operasional satker.",
                status=st,
                masa_berlaku_sip=f"{mulai:%d/%m/%Y} s.d. {akhir:%d/%m/%Y}",
                status_tte=random.choice(["BELUM", "SIAP_TTE", "PROSES_TTE", "SUDAH_TTE", "DITOLAK_TTE"]),
                tanggal_pengajuan=timezone.make_aware(timezone.datetime.combine(mulai, timezone.datetime.min.time())),
                tanggal_persetujuan=timezone.make_aware(timezone.datetime.combine(mulai + timedelta(days=random.randint(1, 10)), timezone.datetime.min.time())) if st in ["DISETUJUI", "TERBIT", "BERAKHIR"] else None,
                disetujui_oleh=user if st in ["DISETUJUI", "TERBIT", "BERAKHIR"] else None,
                catatan="DUMMY-SEED-SIKARIS",
                dibuat_oleh=user,
            )
            try:
                sip.save()
                total += 1
            except Exception:
                # Hindari gagal total karena validasi overlap atau aset rusak berat.
                sip.status = random.choice(["DRAFT", "DIAJUKAN", "BERAKHIR", "DIBATALKAN", "DITOLAK"])
                sip.save()
                total += 1
        return total

    def _seed_service_kendaraan(self, count, kendaraan, user):
        total = 0
        jenis = [x[0] for x in ServiceKendaraan.JENIS_SERVICE]
        for _ in range(count):
            biaya_jasa = money(150000, 5000000, 50000)
            biaya_sparepart = money(0, 25000000, 50000)
            ServiceKendaraan.objects.create(
                kendaraan=random.choice(kendaraan),
                tanggal_service=rand_date(730, 0),
                jenis_service=random.choice(jenis),
                kilometer=random.randint(1000, 220000),
                bengkel=random.choice(["Bengkel Resmi", "Bengkel Rekanan", "Bengkel Umum", "Auto Service"]),
                uraian_pekerjaan="DUMMY-SEED-SIKARIS - pemeriksaan, perawatan, dan penggantian komponen kendaraan.",
                sparepart_diganti=random.choice(["Oli mesin, filter oli", "Ban, kampas rem", "Aki", "Lampu dan wiper", "Tidak ada"]),
                biaya_jasa=biaya_jasa,
                biaya_sparepart=biaya_sparepart,
                kondisi_sebelum=random.choice(["BAIK", "RUSAK_RINGAN"]),
                kondisi_sesudah=random.choice(["BAIK", "RUSAK_RINGAN"]),
                dicatat_oleh=user,
            )
            total += 1
        return total

    def _seed_riwayat_kondisi(self, count, kendaraan, user):
        total = 0
        for _ in range(count):
            RiwayatKondisiKendaraan.objects.create(
                kendaraan=random.choice(kendaraan),
                tanggal=rand_date(730, 0),
                kondisi=random.choice(["BAIK", "RUSAK_RINGAN", "RUSAK_BERAT"]),
                uraian_kondisi="DUMMY-SEED-SIKARIS - hasil pemeriksaan fisik berkala kendaraan.",
                dicatat_oleh=user,
            )
            total += 1
        return total

    def _seed_sip_rumah(self, count, rumah, pegawai, user):
        statuses = ["DRAFT", "DIAJUKAN", "DISETUJUI", "DITOLAK", "TERBIT", "MENUNGGU_TTE", "BERAKHIR", "DIBATALKAN", "PENGOSONGAN"]
        total = 0
        for _ in range(count):
            r = random.choice(rumah)
            p = random.choice([x for x in pegawai if x.unit_kerja_id == r.unit_kerja_id] or pegawai)
            mulai = rand_date(700, 30)
            akhir = add_days(mulai, 180, 1095)
            st = random.choice(statuses)
            sip = SIPRumahDinas(
                tanggal_sip=mulai,
                rumah_dinas=r,
                pegawai=p,
                penghuni=p,
                tanggal_mulai=mulai,
                tanggal_akhir=akhir,
                jenis_masa_berlaku=random.choice(["TANGGAL", "JABATAN"]),
                masa_berlaku_sip=f"{mulai:%d/%m/%Y} s.d. {akhir:%d/%m/%Y}",
                dasar_penerbitan="Surat permohonan pemakaian rumah negara dan hasil verifikasi Biro Umum.",
                jumlah_anggota_keluarga=random.randint(0, 5),
                status=st,
                status_tte=random.choice(["BELUM", "SIAP_TTE", "PROSES_TTE", "SUDAH_TTE", "DITOLAK_TTE"]),
                status_bayar_pnbp=random.choice(["SUDAH_BAYAR", "BELUM_BAYAR", "TIDAK_WAJIB"]),
                tahun_pnbp=mulai.year,
                nilai_pnbp=money(0, 5000000, 50000),
                tanggal_bayar_pnbp=mulai + timedelta(days=random.randint(1, 60)),
                tanggal_pengajuan=timezone.make_aware(timezone.datetime.combine(mulai, timezone.datetime.min.time())),
                tanggal_persetujuan=timezone.make_aware(timezone.datetime.combine(mulai + timedelta(days=random.randint(1, 14)), timezone.datetime.min.time())) if st in ["DISETUJUI", "TERBIT", "BERAKHIR"] else None,
                disetujui_oleh=user if st in ["DISETUJUI", "TERBIT", "BERAKHIR"] else None,
                catatan="DUMMY-SEED-SIKARIS",
                dibuat_oleh=user,
            )
            try:
                sip.save()
                total += 1
            except Exception:
                sip.status = random.choice(["DRAFT", "DIAJUKAN", "BERAKHIR", "DIBATALKAN", "DITOLAK"])
                sip.save()
                total += 1
        return total

    def _seed_perbaikan_rumah(self, count, rumah, pegawai):
        total = 0
        jenis = ["Atap bocor", "Plafon rusak", "Instalasi listrik", "Pipa air", "Pengecatan", "Keramik rusak", "Pintu/jendela rusak"]
        for _ in range(count):
            estimasi = money(500000, 75000000, 50000)
            PerbaikanRumahDinas.objects.create(
                rumah_dinas=random.choice(rumah),
                pelapor=random.choice(pegawai),
                tanggal_laporan=rand_date(730, 0),
                jenis_kerusakan=random.choice(jenis),
                uraian_kerusakan="DUMMY-SEED-SIKARIS - laporan kerusakan dan kebutuhan perbaikan rumah negara.",
                estimasi_biaya=estimasi,
                realisasi_biaya=estimasi + money(0, 10000000, 50000),
                status=random.choice(["Dilaporkan", "Diverifikasi", "Dalam Perbaikan", "Selesai", "Ditolak"]),
            )
            total += 1
        return total

    def _seed_penghapusan(self, count, units, pegawai, kendaraan, rumah, user):
        statuses = [x[0] for x in PermohonanPenghapusanBMN.STATUS_PERMOHONAN if x[0] not in ["DIAJUKAN", "DIVERIFIKASI_BIRO", "DIAJUKAN_SEKJEN", "SK_TERBIT", "DISETUJUI", "PROSES_PENGHAPUSAN"]]
        alasan = [x[0] for x in PermohonanPenghapusanBMN.ALASAN_PENGHAPUSAN]
        total = 0
        for i in range(count):
            jenis_aset = random.choice(["KENDARAAN", "RUMAH_NEGARA", "LAINNYA"])
            unit = random.choice(units)
            kendaraan_obj = random.choice(kendaraan) if jenis_aset == "KENDARAAN" else None
            rumah_obj = random.choice(rumah) if jenis_aset == "RUMAH_NEGARA" else None
            nilai = kendaraan_obj.nilai_perolehan if kendaraan_obj else (rumah_obj.nilai_perolehan if rumah_obj else money(5000000, 250000000))
            nama_barang = str(kendaraan_obj) if kendaraan_obj else (str(rumah_obj) if rumah_obj else random.choice(["Laptop", "Meja kerja", "AC split", "Printer", "Lemari arsip", "Peralatan jaringan"]))
            tgl = rand_date(730, 0)
            status = random.choice(statuses)
            perm = PermohonanPenghapusanBMN.objects.create(
                tanggal_permohonan=tgl,
                unit_kerja=unit,
                pemohon=random.choice([p for p in pegawai if p.unit_kerja_id == unit.id] or pegawai),
                jenis_aset=jenis_aset,
                kendaraan=kendaraan_obj,
                rumah_negara=rumah_obj,
                kode_barang=f"3.{random.randint(1,9):02d}.{random.randint(1,99):02d}.{random.randint(1,999):03d}",
                nup=str(random.randint(1, 9999)),
                nama_barang=nama_barang,
                nilai_perolehan=nilai,
                kondisi_barang=random.choice(["Baik", "Rusak Ringan", "Rusak Berat", "Tidak ditemukan"]),
                lokasi_barang=f"{unit.nama_unit}, {random.choice(KOTA)}",
                alasan_penghapusan=random.choice(alasan),
                uraian_alasan="DUMMY-SEED-SIKARIS - kronologi dan alasan penghapusan BMN untuk data simulasi.",
                dasar_usulan="Hasil inventarisasi, pemeriksaan fisik, dan usulan satker.",
                status=status,
                catatan_unit="DUMMY-SEED-SIKARIS",
                catatan_biro_umum="Catatan verifikasi dummy." if status not in ["DRAFT", "DIAJUKAN_UNIT_KERJA", "MENUNGGU_VERIFIKASI_BIRO_UMUM"] else "",
                diverifikasi_oleh=user if status not in ["DRAFT", "DIAJUKAN_UNIT_KERJA", "MENUNGGU_VERIFIKASI_BIRO_UMUM"] else None,
                tanggal_verifikasi=tgl + timedelta(days=random.randint(1, 7)) if status not in ["DRAFT", "DIAJUKAN_UNIT_KERJA", "MENUNGGU_VERIFIKASI_BIRO_UMUM"] else None,
                nomor_persetujuan=f"B-{random.randint(1000,9999)}/BMN/{tgl.year}" if status in ["DIAJUKAN_KE_SEKJEN", "SK_PENGHAPUSAN_TERBIT", "SELESAI"] else None,
                tanggal_persetujuan=tgl + timedelta(days=random.randint(8, 30)) if status in ["DIAJUKAN_KE_SEKJEN", "SK_PENGHAPUSAN_TERBIT", "SELESAI"] else None,
                nomor_sk_penghapusan=f"{random.randint(1,999)}/HUK/{tgl.year}" if status in ["SK_PENGHAPUSAN_TERBIT", "SELESAI"] else None,
                tanggal_sk_penghapusan=tgl + timedelta(days=random.randint(20, 60)) if status in ["SK_PENGHAPUSAN_TERBIT", "SELESAI"] else None,
                status_tte=random.choice(["BELUM", "SIAP_TTE", "PROSES_TTE", "SUDAH_TTE", "DITOLAK_TTE"]),
                dibuat_oleh=user,
                diperbarui_oleh=user,
            )
            for n in range(random.randint(1, 4)):
                BarangPenghapusanBMN.objects.create(
                    permohonan=perm,
                    nomor_urut=n + 1,
                    kode_barang=perm.kode_barang,
                    nup=str(random.randint(1, 9999)),
                    nama_barang=nama_barang if n == 0 else random.choice(["Laptop", "Printer", "Meja kerja", "AC", "Kursi kerja", "Lemari"]),
                    jenis_aset=jenis_aset,
                    kuantitas=random.randint(1, 10),
                    nilai_perolehan=money(1000000, 250000000),
                    kondisi_barang=random.choice(["Baik", "Rusak Ringan", "Rusak Berat"]),
                    lokasi_barang=perm.lokasi_barang,
                    alasan_penghapusan=perm.alasan_penghapusan,
                    keterangan="DUMMY-SEED-SIKARIS detail barang penghapusan.",
                )
            total += 1
        return total

    def _seed_psp(self, count, units, pegawai, kendaraan, rumah, user):
        statuses = [x[0] for x in PermohonanPSPBMN.STATUS_PERMOHONAN]
        jenis_list = ["KENDARAAN", "RUMAH_NEGARA", "PERALATAN_MESIN", "LAINNYA"]
        total = 0
        for i in range(count):
            jenis = random.choice(jenis_list)
            unit = random.choice(units)
            kendaraan_obj = random.choice(kendaraan) if jenis == "KENDARAAN" else None
            rumah_obj = random.choice(rumah) if jenis == "RUMAH_NEGARA" else None
            nilai = kendaraan_obj.nilai_perolehan if kendaraan_obj else (rumah_obj.nilai_perolehan if rumah_obj else money(5000000, 500000000))
            nama_barang = str(kendaraan_obj) if kendaraan_obj else (str(rumah_obj) if rumah_obj else random.choice(["Peralatan jaringan", "Laptop", "Printer", "Meubelair", "Peralatan kantor"] ))
            tgl = rand_date(730, 0)
            status = random.choice(statuses)
            perm = PermohonanPSPBMN.objects.create(
                tanggal_permohonan=tgl,
                unit_kerja=unit,
                pemohon=random.choice([p for p in pegawai if p.unit_kerja_id == unit.id] or pegawai),
                judul_paket=f"DUMMY-SEED-SIKARIS - PSP {nama_barang}",
                nomor_tiket_siman=f"PP{tgl:%y%m%d}{random.randint(1000000000,9999999999)}",
                kode_satuan_kerja=f"{random.randint(100000,999999)}",
                nama_satuan_kerja=unit.nama_unit,
                jenis_barang=jenis,
                kendaraan=kendaraan_obj,
                rumah_negara=rumah_obj,
                kode_barang=f"3.{random.randint(1,9):02d}.{random.randint(1,99):02d}.{random.randint(1,999):03d}",
                nup=str(random.randint(1, 9999)),
                nama_barang=nama_barang,
                nilai_psp=nilai,
                kondisi_barang=random.choice(["Baik", "Rusak Ringan", "Rusak Berat"]),
                lokasi_barang=f"{unit.nama_unit}, {random.choice(KOTA)}",
                jumlah_barang=1,
                total_nilai_barang=nilai,
                nilai_tertinggi_per_unit=nilai,
                ada_barang_diatas_100jt=nilai > Decimal("100000000"),
                nomor_nota_permohonan_psp=f"ND-{random.randint(100,999)}/PSP/{tgl.year}",
                tanggal_nota_permohonan_psp=tgl,
                nomor_surat_keterangan_digital=f"SKD-{random.randint(100,999)}/{tgl.year}",
                tanggal_surat_keterangan_digital=tgl,
                nomor_surat_pernyataan_formil_materiil=f"SPFM-{random.randint(100,999)}/{tgl.year}",
                tanggal_surat_pernyataan_formil_materiil=tgl,
                nomor_nota_biro_hukum=f"ND-BH-{random.randint(100,999)}/{tgl.year}" if status in ["DIAJUKAN_BIRO_HUKUM", "REVISI_DRAFT_SK", "SK_TERBIT", "SELESAI"] else None,
                tanggal_nota_biro_hukum=tgl + timedelta(days=random.randint(5, 20)) if status in ["DIAJUKAN_BIRO_HUKUM", "REVISI_DRAFT_SK", "SK_TERBIT", "SELESAI"] else None,
                status=status,
                catatan_unit="DUMMY-SEED-SIKARIS",
                catatan_biro_umum="Catatan verifikasi dummy." if status not in ["DRAFT", "VALIDASI_DATA", "DIAJUKAN"] else "",
                catatan_biro_hukum="Catatan biro hukum dummy." if status in ["DIAJUKAN_BIRO_HUKUM", "REVISI_DRAFT_SK", "SK_TERBIT", "SELESAI"] else "",
                diverifikasi_oleh=user if status not in ["DRAFT", "VALIDASI_DATA", "DIAJUKAN"] else None,
                tanggal_verifikasi=tgl + timedelta(days=random.randint(1, 7)) if status not in ["DRAFT", "VALIDASI_DATA", "DIAJUKAN"] else None,
                disetujui_sekjen_oleh=user if status in ["DISETUJUI_SEKJEN", "DIAJUKAN_BIRO_HUKUM", "SK_TERBIT", "SELESAI"] else None,
                tanggal_persetujuan_sekjen=tgl + timedelta(days=random.randint(8, 25)) if status in ["DISETUJUI_SEKJEN", "DIAJUKAN_BIRO_HUKUM", "SK_TERBIT", "SELESAI"] else None,
                nomor_sk_psp=f"{random.randint(1,999)}/HUK/{tgl.year}" if status in ["SK_TERBIT", "SELESAI"] else None,
                tanggal_sk_psp=tgl + timedelta(days=random.randint(25, 70)) if status in ["SK_TERBIT", "SELESAI"] else None,
                status_tte=random.choice(["BELUM", "SIAP_TTE", "PROSES_TTE", "SUDAH_TTE", "DITOLAK_TTE"]),
                status_emeterai=random.choice(["TIDAK_WAJIB", "BELUM", "SUDAH", "GAGAL"]),
                nomor_serial_emeterai=f"EM{random.randint(1000000000,9999999999)}" if random.choice([True, False]) else None,
                dibuat_oleh=user,
                diperbarui_oleh=user,
            )
            for n in range(random.randint(1, 5)):
                nilai_item = money(1000000, 250000000)
                qty = random.randint(1, 20)
                BarangPSP.objects.create(
                    permohonan=perm,
                    nomor_urut=n + 1,
                    kode_satuan_kerja=perm.kode_satuan_kerja,
                    nama_satuan_kerja=perm.nama_satuan_kerja,
                    kode_barang=f"{perm.kode_barang}.{n+1:03d}",
                    nup=f"{random.randint(1, 9999)}-{n+1}",
                    nama_barang=nama_barang if n == 0 else random.choice(["Laptop", "Printer", "Switch jaringan", "Meja kerja", "Kursi kerja", "Lemari arsip"]),
                    tipe_barang=random.choice(["Unit", "Paket", "Set", "Standar"]),
                    tahun_perolehan=str(random.randint(2015, 2025)),
                    kuantitas=qty,
                    nilai_perolehan=nilai_item,
                    kondisi_barang=random.choice(["BAIK", "RUSAK_RINGAN", "RUSAK_BERAT"]),
                    keterangan="DUMMY-SEED-SIKARIS detail barang PSP. Lokasi: " + str(perm.lokasi_barang),
                )
            perm.refresh_rekap_barang(commit=True)
            total += 1
        return total
