from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from core.models import next_nomor_surat
from master.models import Kendaraan, Pegawai, RumahDinas, TimeStampedModel, UnitKerja


class PermohonanPSPBMN(TimeStampedModel):
    JENIS_BARANG = [
        ('KENDARAAN', 'Kendaraan'),
        ('RUMAH_NEGARA', 'Rumah Negara'),
        ('TANAH_NEGARA', 'Tanah Negara'),
        ('PERALATAN_MESIN', 'Peralatan dan Mesin'),
        ('LAINNYA', 'BMN Lainnya'),
    ]

    STATUS_PERMOHONAN = [
        ('DRAFT', 'Draft'),
        ('VALIDASI_DATA', 'Validasi Data'),
        ('DIAJUKAN', 'Diajukan Unit Kerja'),
        ('DIVERIFIKASI_BIRO', 'Diverifikasi Biro Umum'),
        ('PERLU_PERBAIKAN', 'Perlu Perbaikan Usulan'),
        ('SIAP_DIAJUKAN_SEKJEN', 'Siap Diajukan ke Sekjen'),
        ('DIAJUKAN_SEKJEN', 'Diajukan ke Sekjen'),
        ('DISETUJUI_SEKJEN', 'Disetujui Sekjen'),
        ('DIAJUKAN_BIRO_HUKUM', 'Diajukan ke Biro Hukum'),
        ('REVISI_DRAFT_SK', 'Revisi Draf SK'),
        ('SK_TERBIT', 'SK PSP Terbit'),
        ('DITOLAK', 'Ditolak'),
        ('DISETUJUI', 'Disetujui'),
        ('PROSES_PSP', 'Proses Penetapan PSP'),
        ('SELESAI', 'Selesai'),
    ]

    STATUS_TTE = [
        ('BELUM', 'Menunggu Penetapan'),
        ('SIAP_TTE', 'Siap TTE BSrE'),
        ('PROSES_TTE', 'Proses TTE BSrE'),
        ('SUDAH_TTE', 'Sudah TTE BSrE'),
        ('DITOLAK_TTE', 'Ditolak TTE BSrE'),
    ]

    STATUS_EMETERAI = [
        ('TIDAK_WAJIB', 'Tidak Wajib'),
        ('BELUM', 'Belum e-Meterai'),
        ('SUDAH', 'Sudah e-Meterai'),
        ('GAGAL', 'Gagal/Perlu Perbaikan'),
    ]

    nomor_permohonan = models.CharField(max_length=120, unique=True, blank=True)
    tanggal_permohonan = models.DateField(default=timezone.now)
    unit_kerja = models.ForeignKey(UnitKerja, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')
    pemohon = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')

    # Header paket usulan banyak barang.
    judul_paket = models.CharField(max_length=250, blank=True, null=True, help_text='Contoh: PSP BMN Berupa 3.000 Unit Peralatan dan Mesin pada Sekretariat Jenderal')
    nomor_tiket_siman = models.CharField(max_length=80, blank=True, null=True, help_text='Nomor tiket terdaftar pada SIMAN V2, contoh: PP126010610424145813')
    kode_satuan_kerja = models.CharField(max_length=120, blank=True, null=True)
    nama_satuan_kerja = models.CharField(max_length=220, blank=True, null=True)
    batas_nilai_per_unit = models.DecimalField(max_digits=20, decimal_places=2, default=100000000)

    jenis_barang = models.CharField(max_length=30, choices=JENIS_BARANG)
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')
    rumah_negara = models.ForeignKey(RumahDinas, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')
    tanah_negara = models.ForeignKey('tanah_negara.TanahNegara', on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')

    # Snapshot barang tunggal. Tetap dipertahankan agar kompatibel dengan modul lama.
    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    nup = models.CharField(max_length=100, blank=True, null=True)
    nama_barang = models.CharField(max_length=220, blank=True, null=True)
    nilai_psp = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    kondisi_barang = models.CharField(max_length=120, blank=True, null=True)
    lokasi_barang = models.TextField(blank=True, null=True)
    keterangan_barang = models.TextField(blank=True, null=True)

    jumlah_barang = models.PositiveIntegerField(default=0)
    total_nilai_barang = models.DecimalField(max_digits=24, decimal_places=2, default=0)
    nilai_tertinggi_per_unit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    ada_barang_diatas_100jt = models.BooleanField(default=False)

    # Nomor surat disimpan untuk monitoring. Pada dokumen Word hasil generate, nomor dapat diedit manual.
    nomor_nota_permohonan_psp = models.CharField(max_length=120, blank=True, null=True, help_text='Nomor dapat diedit manual pada dokumen Word hasil generate.')
    tanggal_nota_permohonan_psp = models.DateField(blank=True, null=True)
    nomor_surat_keterangan_digital = models.CharField(max_length=120, blank=True, null=True)
    tanggal_surat_keterangan_digital = models.DateField(blank=True, null=True)
    nomor_surat_pernyataan_formil_materiil = models.CharField(max_length=120, blank=True, null=True)
    tanggal_surat_pernyataan_formil_materiil = models.DateField(blank=True, null=True)
    nomor_nota_biro_hukum = models.CharField(max_length=120, blank=True, null=True)
    tanggal_nota_biro_hukum = models.DateField(blank=True, null=True)

    # Dokumen PSP SIKARIS final/gabungan dalam satu file PDF sebelum diteruskan ke Sekjen.
    dokumen_permohonan_psp = models.FileField(upload_to='psp/dokumen_permohonan/', blank=True, null=True, help_text='Gabungan surat permohonan, pengantar, daftar kondisi, laporan sub kelompok, dan surat pernyataan dalam satu PDF.')

    # Dokumen dasar PSP.
    surat_permohonan_satker = models.FileField(upload_to='psp/surat_permohonan_satker/', blank=True, null=True)
    surat_pengantar_eselon1 = models.FileField(upload_to='psp/surat_pengantar_eselon1/', blank=True, null=True)
    daftar_kondisi_barang = models.FileField(upload_to='psp/daftar_kondisi_barang/', blank=True, null=True)
    laporan_sub_kelompok_barang = models.FileField(upload_to='psp/laporan_sub_kelompok_barang/', blank=True, null=True)
    surat_pernyataan_kepala_satker = models.FileField(upload_to='psp/surat_pernyataan_kepala_satker/', blank=True, null=True)

    # Dokumen tambahan kendaraan > Rp100 juta.
    foto_kendaraan = models.FileField(upload_to='psp/foto_kendaraan/', blank=True, null=True)
    dokumen_kepemilikan = models.FileField(upload_to='psp/dokumen_kepemilikan/', blank=True, null=True)
    surat_pernyataan_pengganti_kepemilikan = models.FileField(upload_to='psp/surat_pernyataan_pengganti_kepemilikan/', blank=True, null=True)

    status = models.CharField(max_length=40, choices=STATUS_PERMOHONAN, default='DIAJUKAN')
    catatan_unit = models.TextField(blank=True, null=True)
    catatan_biro_umum = models.TextField(blank=True, null=True)
    catatan_biro_hukum = models.TextField(blank=True, null=True)

    diverifikasi_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifikasi_psp')
    tanggal_verifikasi = models.DateField(blank=True, null=True)
    disetujui_sekjen_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='psp_disetujui_sekjen')
    tanggal_persetujuan_sekjen = models.DateField(blank=True, null=True)
    nomor_sk_psp = models.CharField(max_length=150, blank=True, null=True, help_text='Format otomatis SK: nomor/HUK/tahun')
    tanggal_sk_psp = models.DateField(blank=True, null=True)
    sk_penetapan_psp = models.FileField(upload_to='psp/penetapan_psp/', blank=True, null=True)

    # Berkas yang akan/ sudah ditandatangani elektronik BSrE.
    status_tte = models.CharField(max_length=20, choices=STATUS_TTE, default='BELUM')
    pejabat_tte = models.CharField(max_length=180, blank=True, null=True, help_text='Nama/jabatan pejabat TTE BSrE')
    nip_pejabat_tte = models.CharField(max_length=30, blank=True, null=True)
    tanggal_tte = models.DateTimeField(blank=True, null=True)
    file_sebelum_tte = models.FileField(upload_to='psp/tte/sebelum/', blank=True, null=True)
    file_setelah_tte = models.FileField(upload_to='psp/tte/setelah/', blank=True, null=True)

    # e-Meterai untuk dokumen pernyataan/bermeterai.
    status_emeterai = models.CharField(max_length=20, choices=STATUS_EMETERAI, default='TIDAK_WAJIB')
    nomor_serial_emeterai = models.CharField(max_length=120, blank=True, null=True)
    tanggal_emeterai = models.DateTimeField(blank=True, null=True)
    dokumen_bermeterai = models.FileField(upload_to='psp/emeterai/', blank=True, null=True)

    dibuat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp_dibuat')
    diperbarui_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp_diperbarui')

    class Meta:
        ordering = ['-tanggal_permohonan', '-created_at']
        verbose_name = 'Permohonan PSP BMN'
        verbose_name_plural = 'Permohonan PSP BMN'

    def __str__(self):
        return f'{self.nomor_permohonan or "Permohonan PSP"} - {self.judul_paket or self.nama_barang or self.get_jenis_barang_display()}'

    @property
    def is_kendaraan_diatas_100jt(self):
        try:
            return self.jenis_barang == 'KENDARAAN' and self.nilai_psp and self.nilai_psp > 100000000
        except Exception:
            return False

    @property
    def is_paket_banyak_barang(self):
        return self.detail_barang.exists()

    @property
    def kategori_nilai_display(self):
        if self.ada_barang_diatas_100jt:
            return 'Ada barang di atas Rp100 juta'
        if self.is_kendaraan_diatas_100jt:
            return 'Kendaraan di atas Rp100 juta'
        return 'Semua barang ≤ Rp100 juta'

    @property
    def kelengkapan_dokumen(self):
        items = [
            ('Dokumen PSP SIKARIS Final/Gabungan', bool(self.dokumen_permohonan_psp)),
            ('Surat Permohonan Satker', bool(self.surat_permohonan_satker)),
            ('Surat Pengantar Eselon I', bool(self.surat_pengantar_eselon1)),
            ('Daftar Kondisi Barang', bool(self.daftar_kondisi_barang)),
            ('Laporan Sub-Sub Kelompok', bool(self.laporan_sub_kelompok_barang)),
            ('Surat Pernyataan Kepala Satker', bool(self.surat_pernyataan_kepala_satker)),
        ]
        if self.ada_barang_diatas_100jt or self.is_kendaraan_diatas_100jt:
            items.append(('Dokumen Kepemilikan / Surat Pernyataan Pengganti', bool(self.dokumen_kepemilikan or self.surat_pernyataan_pengganti_kepemilikan)))
        return items

    @property
    def dokumen_wajib_lengkap(self):
        return all(ok for _label, ok in self.kelengkapan_dokumen)

    def refresh_rekap_barang(self, commit=True):
        qs = self.detail_barang.all()
        if qs.exists():
            agg = qs.aggregate(total=Sum('nilai_total'))
            self.jumlah_barang = sum([x.kuantitas or 0 for x in qs])
            self.total_nilai_barang = agg['total'] or Decimal('0')
            self.nilai_tertinggi_per_unit = max([x.nilai_perolehan or Decimal('0') for x in qs] or [Decimal('0')])
            self.ada_barang_diatas_100jt = qs.filter(nilai_perolehan__gt=self.batas_nilai_per_unit).exists()
            self.nilai_psp = self.total_nilai_barang
        else:
            self.jumlah_barang = 1 if self.nilai_psp else 0
            self.total_nilai_barang = self.nilai_psp or Decimal('0')
            self.nilai_tertinggi_per_unit = self.nilai_psp or Decimal('0')
            self.ada_barang_diatas_100jt = bool(self.nilai_psp and self.nilai_psp > self.batas_nilai_per_unit)
        if commit and self.pk:
            self.save(update_fields=['jumlah_barang', 'total_nilai_barang', 'nilai_tertinggi_per_unit', 'ada_barang_diatas_100jt', 'nilai_psp', 'updated_at'])

    @property
    def tanggal_akhir_proses(self):
        return self.tanggal_sk_psp or self.tanggal_persetujuan_sekjen or self.tanggal_verifikasi or timezone.now().date()

    @property
    def lama_proses_hari(self):
        if not self.tanggal_permohonan:
            return 0
        try:
            return max((self.tanggal_akhir_proses - self.tanggal_permohonan).days, 0)
        except Exception:
            return 0

    @property
    def status_pengingat_class(self):
        if self.status in ['SELESAI', 'DITOLAK', 'SK_TERBIT']:
            return 'success'
        if self.status in ['PERLU_PERBAIKAN', 'REVISI_DRAFT_SK']:
            return 'warning' if self.lama_proses_hari <= 7 else 'danger'
        if self.status in ['DIAJUKAN', 'VALIDASI_DATA']:
            if self.lama_proses_hari >= 7:
                return 'danger'
            if self.lama_proses_hari >= 3:
                return 'warning'
            return 'success'
        if self.status in ['DIVERIFIKASI_BIRO', 'DISETUJUI', 'PROSES_PSP', 'SIAP_DIAJUKAN_SEKJEN', 'DIAJUKAN_SEKJEN', 'DISETUJUI_SEKJEN', 'DIAJUKAN_BIRO_HUKUM']:
            if self.lama_proses_hari >= 14:
                return 'danger'
            if self.lama_proses_hari >= 7:
                return 'warning'
            return 'success'
        return 'success'

    @property
    def status_pengingat_label(self):
        if self.status in ['SELESAI', 'SK_TERBIT']:
            return 'Selesai / SK PSP Terbit'
        if self.status == 'DITOLAK':
            return 'Ditolak'
        if self.status in ['PERLU_PERBAIKAN', 'REVISI_DRAFT_SK']:
            return 'Menunggu perbaikan/revisi'
        if self.status in ['DIAJUKAN', 'VALIDASI_DATA']:
            return 'Menunggu verifikasi Biro Umum'
        if self.status == 'DIAJUKAN_SEKJEN':
            return 'Menunggu persetujuan Sekjen'
        if self.status == 'DIAJUKAN_BIRO_HUKUM':
            return 'Menunggu proses Biro Hukum'
        return 'Dalam proses'

    @property
    def pesan_pengingat_pemohon(self):
        if self.status == 'PERLU_PERBAIKAN':
            return 'Pemohon/Satker perlu memperbaiki atau melengkapi dokumen PSP sesuai catatan Biro Umum.'
        if self.status == 'DIAJUKAN':
            return 'Permohonan PSP sudah dikirim ke Biro Umum. Pantau status dan lengkapi dokumen bila diminta.'
        return ''

    @property
    def pesan_pengingat_verifikator(self):
        if self.status in ['DIAJUKAN', 'VALIDASI_DATA'] and self.lama_proses_hari >= 3:
            return 'Pengingat untuk Biro Umum: permohonan PSP sudah menunggu verifikasi beberapa hari.'
        if self.status in ['DIVERIFIKASI_BIRO', 'DISETUJUI', 'PROSES_PSP', 'DIAJUKAN_SEKJEN', 'DIAJUKAN_BIRO_HUKUM'] and self.lama_proses_hari >= 7:
            return 'Pengingat: permohonan PSP perlu tindak lanjut penetapan/dokumen.'
        return ''

    @property
    def status_dokumen_final_display(self):
        """Label aman untuk ditampilkan di UI agar tidak mengesankan sistem memvalidasi BSrE."""
        if self.status in ['SK_TERBIT', 'SELESAI']:
            if self.status_tte == 'SUDAH_TTE':
                return 'SK PSP Terbit - Sudah TTE BSrE'
            if self.sk_penetapan_psp:
                return 'SK PSP Terbit - SK Final Diunggah'
            return 'SK PSP Terbit'
        if self.status in ['DIAJUKAN_SEKJEN', 'SIAP_DIAJUKAN_SEKJEN', 'DISETUJUI_SEKJEN']:
            if self.sk_penetapan_psp:
                return 'SK Final Diunggah'
            return 'Menunggu Penetapan Sekjen'
        if self.status_tte == 'SUDAH_TTE':
            return 'Dokumen Sudah TTE BSrE'
        return 'Menunggu Penetapan'

    def _generate_nomor_dokumen(self):
        tanggal = self.tanggal_permohonan or timezone.now().date()
        if not self.nomor_permohonan:
            self.nomor_permohonan = next_nomor_surat('PSP-BMN', tanggal, format_surat='SIMPLE')
        if not self.nomor_nota_permohonan_psp:
            self.nomor_nota_permohonan_psp = next_nomor_surat('NOTA_PSP_SEKJEN', self.tanggal_nota_permohonan_psp or tanggal)
        if not self.nomor_surat_keterangan_digital:
            self.nomor_surat_keterangan_digital = next_nomor_surat('KET_DIGITAL_PSP', self.tanggal_surat_keterangan_digital or tanggal)
        if not self.nomor_surat_pernyataan_formil_materiil:
            self.nomor_surat_pernyataan_formil_materiil = next_nomor_surat('PERNYATAAN_FORMIL_MATERIIL_PSP', self.tanggal_surat_pernyataan_formil_materiil or tanggal)
        if self.status in ['DIAJUKAN_BIRO_HUKUM', 'REVISI_DRAFT_SK', 'SK_TERBIT', 'SELESAI'] and not self.nomor_nota_biro_hukum:
            self.nomor_nota_biro_hukum = next_nomor_surat('NOTA_PSP_BIRO_HUKUM', self.tanggal_nota_biro_hukum or tanggal)
        if self.status in ['SK_TERBIT', 'SELESAI'] and not self.nomor_sk_psp:
            self.nomor_sk_psp = next_nomor_surat('SK_PSP', self.tanggal_sk_psp or tanggal, format_surat='HUK')

    def save(self, *args, **kwargs):
        self._generate_nomor_dokumen()
        if not self.tanggal_nota_permohonan_psp:
            self.tanggal_nota_permohonan_psp = self.tanggal_permohonan
        if not self.tanggal_surat_keterangan_digital:
            self.tanggal_surat_keterangan_digital = self.tanggal_permohonan
        if not self.tanggal_surat_pernyataan_formil_materiil:
            self.tanggal_surat_pernyataan_formil_materiil = self.tanggal_permohonan
        if not self.pejabat_tte and self.status in ['SK_TERBIT', 'SELESAI']:
            self.pejabat_tte = 'Sekretaris Jenderal a.n. Menteri Sosial (TTE BSrE)'
        super().save(*args, **kwargs)


class BarangPSP(TimeStampedModel):
    KONDISI_CHOICES = [
        ('BAIK', 'Baik'),
        ('RUSAK_RINGAN', 'Rusak Ringan'),
        ('RUSAK_BERAT', 'Rusak Berat'),
        ('LAINNYA', 'Lainnya'),
    ]

    permohonan = models.ForeignKey(PermohonanPSPBMN, on_delete=models.CASCADE, related_name='detail_barang')
    nomor_urut = models.PositiveIntegerField(default=1)
    kode_satuan_kerja = models.CharField(max_length=120, blank=True, null=True)
    nama_satuan_kerja = models.CharField(max_length=220, blank=True, null=True)
    kode_barang = models.CharField(max_length=100)
    nup = models.CharField(max_length=100)
    nama_barang = models.CharField(max_length=220)
    tipe_barang = models.CharField(max_length=250, blank=True, null=True)
    tahun_perolehan = models.CharField(max_length=30, blank=True, null=True)
    kuantitas = models.PositiveIntegerField(default=1)
    nilai_perolehan = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    nilai_total = models.DecimalField(max_digits=22, decimal_places=2, default=0)
    kondisi_barang = models.CharField(max_length=30, choices=KONDISI_CHOICES, default='BAIK')
    keterangan = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['nomor_urut', 'id']
        unique_together = ('permohonan', 'kode_barang', 'nup')
        verbose_name = 'Detail Barang PSP'
        verbose_name_plural = 'Detail Barang PSP'

    def save(self, *args, **kwargs):
        self.nilai_total = (self.nilai_perolehan or Decimal('0')) * (self.kuantitas or 0)
        super().save(*args, **kwargs)
        if self.permohonan_id:
            self.permohonan.refresh_rekap_barang(commit=True)

    def delete(self, *args, **kwargs):
        permohonan = self.permohonan
        result = super().delete(*args, **kwargs)
        if permohonan and permohonan.pk:
            permohonan.refresh_rekap_barang(commit=True)
        return result

    def __str__(self):
        return f'{self.kode_barang} - {self.nup} - {self.nama_barang}'


class FotoBarangPSP(TimeStampedModel):
    permohonan = models.ForeignKey(
        PermohonanPSPBMN,
        on_delete=models.CASCADE,
        related_name='foto_barang_list'
    )
    foto = models.ImageField(upload_to='psp/foto_barang/')
    keterangan = models.CharField(max_length=200, blank=True, null=True)
    diupload_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Foto Barang PSP'
        verbose_name_plural = 'Foto Barang PSP'

    def __str__(self):
        return f'Foto PSP {self.permohonan.nomor_permohonan or self.permohonan_id}'
