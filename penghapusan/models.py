from django.conf import settings
from django.db import models
from django.utils import timezone

from master.models import Kendaraan, RumahDinas, Pegawai, TimeStampedModel, UnitKerja

try:
    from tanah_negara.models import TanahNegara
except Exception:  # pragma: no cover
    TanahNegara = None


class PermohonanPenghapusanBMN(TimeStampedModel):
    JENIS_ASET = [
        ('KENDARAAN', 'Kendaraan'),
        ('RUMAH_NEGARA', 'Rumah Negara'),
        ('TANAH_NEGARA', 'Tanah Negara'),
        ('LAINNYA', 'BMN Lainnya'),
    ]

    ALASAN_PENGHAPUSAN = [
        ('RUSAK_BERAT', 'Rusak Berat'),
        ('HILANG', 'Hilang'),
        ('MUSNAH', 'Musnah'),
        ('TIDAK_EKONOMIS', 'Tidak Ekonomis untuk Diperbaiki'),
        ('IDLE_TIDAK_DIGUNAKAN', 'Idle/Tidak Digunakan'),
        ('PENYERAHAN_PENGELOLA', 'Penyerahan kepada Pengelola Barang'),
        ('ALIH_STATUS', 'Alih Status Penggunaan'),
        ('PEMINDAHTANGANAN', 'Pemindahtanganan'),
        ('LAINNYA', 'Lainnya'),
    ]

    STATUS_PERMOHONAN = [
        ('DRAFT', 'Draft/Konsep'),
        ('DIAJUKAN_UNIT_KERJA', 'Diajukan Unit Kerja'),
        ('MENUNGGU_VERIFIKASI_BIRO_UMUM', 'Menunggu Verifikasi Biro Umum'),
        ('DIVERIFIKASI_BIRO_UMUM', 'Diverifikasi Biro Umum'),
        ('PERLU_PERBAIKAN', 'Perlu Perbaikan Usulan'),
        ('DIAJUKAN_KE_DIRJEN_REHSOS', 'Diajukan ke Dirjen Rehsos'),
        ('DISETUJUI_DIRJEN_REHSOS', 'Disetujui Dirjen Rehsos'),
        ('DITOLAK_DIRJEN_REHSOS', 'Ditolak Dirjen Rehsos'),
        ('DIAJUKAN_KE_SEKJEN', 'Diajukan ke Sekjen'),
        ('DITOLAK_SEKJEN', 'Ditolak Sekjen'),
        ('SK_PENGHAPUSAN_TERBIT', 'SK Penghapusan Terbit'),
        ('SELESAI', 'Selesai/Dihapuskan'),
        # Alias status lama agar data existing tetap terbaca rapi.
        ('DIAJUKAN', 'Diajukan Unit Kerja'),
        ('DIVERIFIKASI_BIRO', 'Diverifikasi Biro Umum'),
        ('DIAJUKAN_SEKJEN', 'Diajukan ke Sekjen'),
        ('SK_TERBIT', 'SK Penghapusan Terbit'),
        ('DITOLAK', 'Ditolak'),
        ('DISETUJUI', 'Disetujui'),
        ('PROSES_PENGHAPUSAN', 'Proses Penghapusan'),
    ]

    nomor_permohonan = models.CharField(max_length=120, unique=True, blank=True)
    tanggal_permohonan = models.DateField(default=timezone.now)
    unit_kerja = models.ForeignKey(UnitKerja, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_penghapusan')
    pemohon = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_penghapusan')

    jenis_aset = models.CharField(max_length=30, choices=JENIS_ASET)
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_penghapusan')
    rumah_negara = models.ForeignKey(RumahDinas, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_penghapusan')
    tanah_negara = models.ForeignKey('tanah_negara.TanahNegara', on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_penghapusan')

    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    nup = models.CharField(max_length=100, blank=True, null=True)
    nama_barang = models.CharField(max_length=220)
    nilai_perolehan = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    kondisi_barang = models.CharField(max_length=120, blank=True, null=True)
    lokasi_barang = models.TextField(blank=True, null=True)

    alasan_penghapusan = models.CharField(max_length=40, choices=ALASAN_PENGHAPUSAN)
    uraian_alasan = models.TextField('Uraian Alasan/Kronologi')
    dasar_usulan = models.TextField('Dasar Usulan', blank=True, null=True, help_text='Contoh: hasil pemeriksaan fisik, rusak berat, idle, hilang, atau dasar administratif lain.')

    dokumen_usulan = models.FileField(upload_to='penghapusan/usulan/', blank=True, null=True, help_text='Surat usulan/nota dinas dari unit kerja.')
    dokumen_pendukung = models.FileField(upload_to='penghapusan/pendukung/', blank=True, null=True, help_text='BA pemeriksaan, foto kondisi, dokumen kepemilikan, atau lampiran lain.')
    foto_kondisi = models.ImageField(upload_to='penghapusan/foto/', blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_PERMOHONAN, default='MENUNGGU_VERIFIKASI_BIRO_UMUM')
    catatan_unit = models.TextField(blank=True, null=True)
    catatan_biro_umum = models.TextField(blank=True, null=True)

    diverifikasi_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifikasi_penghapusan')
    tanggal_verifikasi = models.DateField(blank=True, null=True)
    nomor_persetujuan = models.CharField(max_length=150, blank=True, null=True)
    tanggal_persetujuan = models.DateField(blank=True, null=True)
    dokumen_persetujuan = models.FileField(upload_to='penghapusan/persetujuan/', blank=True, null=True)
    nomor_sk_penghapusan = models.CharField(max_length=150, blank=True, null=True)
    tanggal_sk_penghapusan = models.DateField(blank=True, null=True)
    dokumen_sk_penghapusan = models.FileField(upload_to='penghapusan/sk/', blank=True, null=True)
    berita_acara_penghapusan = models.FileField(upload_to='penghapusan/ba/', blank=True, null=True)
    status_tte = models.CharField(max_length=20, choices=[('BELUM', 'Belum TTE'), ('SIAP_TTE', 'Siap TTE'), ('PROSES_TTE', 'Proses TTE'), ('SUDAH_TTE', 'Sudah TTE'), ('DITOLAK_TTE', 'Ditolak TTE')], default='BELUM')
    pejabat_tte = models.CharField(max_length=180, blank=True, null=True)
    nip_pejabat_tte = models.CharField(max_length=30, blank=True, null=True)
    tanggal_tte = models.DateTimeField(blank=True, null=True)
    file_sebelum_tte = models.FileField(upload_to='penghapusan/tte/sebelum/', blank=True, null=True)
    file_setelah_tte = models.FileField(upload_to='penghapusan/tte/setelah/', blank=True, null=True)
    catatan_tte = models.TextField(blank=True, null=True)

    dibuat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_penghapusan_dibuat')
    diperbarui_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_penghapusan_diperbarui')

    class Meta:
        ordering = ['-tanggal_permohonan', '-created_at']
        verbose_name = 'Permohonan Penghapusan BMN'
        verbose_name_plural = 'Permohonan Penghapusan BMN'

    def __str__(self):
        return f'{self.nomor_permohonan or "Permohonan"} - {self.nama_barang}'



    @property
    def tanggal_akhir_proses(self):
        """Tanggal acuan akhir proses untuk menghitung lama proses."""
        return (
            self.tanggal_sk_penghapusan
            or self.tanggal_persetujuan
            or self.tanggal_verifikasi
            or timezone.now().date()
        )

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
        """Kelas visual SLA: aman, perhatian, terlambat."""
        st = self.status_norm
        if st in ['SELESAI', 'SK_PENGHAPUSAN_TERBIT']:
            return 'success'
        if st in ['DITOLAK_SEKJEN', 'DITOLAK_DIRJEN_REHSOS']:
            return 'danger'
        if st == 'PERLU_PERBAIKAN':
            return 'warning' if self.lama_proses_hari <= 7 else 'danger'
        if st in ['DIAJUKAN_UNIT_KERJA', 'MENUNGGU_VERIFIKASI_BIRO_UMUM']:
            if self.lama_proses_hari >= 7:
                return 'danger'
            if self.lama_proses_hari >= 3:
                return 'warning'
            return 'success'
        if st in ['DIVERIFIKASI_BIRO_UMUM', 'DIAJUKAN_KE_DIRJEN_REHSOS', 'DISETUJUI_DIRJEN_REHSOS', 'DIAJUKAN_KE_SEKJEN']:
            if self.lama_proses_hari >= 14:
                return 'danger'
            if self.lama_proses_hari >= 7:
                return 'warning'
            return 'success'
        return 'success'

    @property
    def status_pengingat_label(self):
        st = self.status_norm
        if st in ['SELESAI', 'SK_PENGHAPUSAN_TERBIT']:
            return 'Selesai / SK Penghapusan Terbit'
        if st == 'DITOLAK_SEKJEN':
            return 'Ditolak Sekjen'
        if st == 'DITOLAK_DIRJEN_REHSOS':
            return 'Ditolak Dirjen Rehsos'
        if st == 'PERLU_PERBAIKAN':
            return 'Menunggu perbaikan Satker'
        if st in ['DIAJUKAN_UNIT_KERJA', 'MENUNGGU_VERIFIKASI_BIRO_UMUM']:
            if self.lama_proses_hari >= 7:
                return 'Terlambat diverifikasi'
            if self.lama_proses_hari >= 3:
                return 'Perlu segera diverifikasi'
            return 'Menunggu verifikasi Biro Umum'
        if st == 'DIVERIFIKASI_BIRO_UMUM':
            return 'Diverifikasi Biro Umum'
        if st == 'DIAJUKAN_KE_DIRJEN_REHSOS':
            return 'Menunggu persetujuan Dirjen Rehsos'
        if st == 'DISETUJUI_DIRJEN_REHSOS':
            return 'Disetujui Dirjen Rehsos, siap diteruskan ke Sekjen'
        if st == 'DIAJUKAN_KE_SEKJEN':
            return 'Menunggu penetapan SK Sekjen'
        return 'Dalam proses'

    @property
    def pesan_pengingat_pemohon(self):
        if self.status == 'PERLU_PERBAIKAN':
            return 'Pemohon/Satker perlu segera memperbaiki atau melengkapi usulan sesuai catatan Biro Umum.'
        if self.status_norm in ['DIAJUKAN_UNIT_KERJA', 'MENUNGGU_VERIFIKASI_BIRO_UMUM']:
            return 'Usulan sudah dikirim ke Biro Umum. Pantau status dan lengkapi dokumen bila diminta.'
        return ''

    @property
    def pesan_pengingat_verifikator(self):
        if self.status_norm in ['DIAJUKAN_UNIT_KERJA', 'MENUNGGU_VERIFIKASI_BIRO_UMUM'] and self.lama_proses_hari >= 3:
            return 'Pengingat untuk Biro Umum: permohonan sudah menunggu verifikasi beberapa hari.'
        if self.status_norm in ['DIVERIFIKASI_BIRO_UMUM', 'DIAJUKAN_KE_DIRJEN_REHSOS', 'DISETUJUI_DIRJEN_REHSOS', 'DIAJUKAN_KE_SEKJEN'] and self.lama_proses_hari >= 7:
            return 'Pengingat untuk Biro Umum: permohonan perlu tindak lanjut proses/persetujuan/SK/BA.'
        return ''


    @property
    def status_norm(self):
        """Normalisasi status lama ke status alur baru agar dashboard/list/detail konsisten."""
        alias = {
            'DIAJUKAN': 'MENUNGGU_VERIFIKASI_BIRO_UMUM',
            'DIVERIFIKASI_BIRO': 'DIVERIFIKASI_BIRO_UMUM',
            'DIAJUKAN_SEKJEN': 'DIAJUKAN_KE_SEKJEN',
            'SK_TERBIT': 'SK_PENGHAPUSAN_TERBIT',
            'DITOLAK': 'DITOLAK_SEKJEN',
            'DISETUJUI': 'DIAJUKAN_KE_SEKJEN',
            'PROSES_PENGHAPUSAN': 'DIAJUKAN_KE_SEKJEN',
        }
        return alias.get(self.status, self.status)

    @property
    def status_label_alur(self):
        labels = dict(self.STATUS_PERMOHONAN)
        return labels.get(self.status_norm, self.get_status_display())

    @property
    def sudah_final(self):
        return self.status_norm in ['SK_PENGHAPUSAN_TERBIT', 'SELESAI']

    def save(self, *args, **kwargs):
        if not self.nomor_permohonan:
            super().save(*args, **kwargs)
            self.nomor_permohonan = f'UP-BMN/{self.tanggal_permohonan:%Y}/{self.pk:05d}'
            kwargs['force_insert'] = False
            kwargs['force_update'] = True
        super().save(*args, **kwargs)


class FotoKondisiPenghapusanBMN(TimeStampedModel):
    permohonan = models.ForeignKey(
        PermohonanPenghapusanBMN,
        on_delete=models.CASCADE,
        related_name='foto_kondisi_list'
    )
    foto = models.ImageField(upload_to='penghapusan/foto_multi/')
    keterangan = models.CharField(max_length=200, blank=True, null=True)
    diupload_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Foto Kondisi Penghapusan BMN'
        verbose_name_plural = 'Foto Kondisi Penghapusan BMN'

    def __str__(self):
        return f'Foto {self.permohonan.nomor_permohonan or self.permohonan_id}'


class BarangPenghapusanBMN(TimeStampedModel):
    permohonan = models.ForeignKey(
        PermohonanPenghapusanBMN,
        on_delete=models.CASCADE,
        related_name='detail_barang'
    )
    nomor_urut = models.PositiveIntegerField(default=1)
    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    nup = models.CharField(max_length=100, blank=True, null=True)
    nama_barang = models.CharField(max_length=220)
    jenis_aset = models.CharField(max_length=30, choices=PermohonanPenghapusanBMN.JENIS_ASET, default='LAINNYA')
    kuantitas = models.PositiveIntegerField(default=1)
    nilai_perolehan = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    kondisi_barang = models.CharField(max_length=120, blank=True, null=True)
    lokasi_barang = models.TextField(blank=True, null=True)
    alasan_penghapusan = models.CharField(max_length=40, choices=PermohonanPenghapusanBMN.ALASAN_PENGHAPUSAN, default='RUSAK_BERAT')
    keterangan = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['nomor_urut', 'id']
        verbose_name = 'Detail Barang Penghapusan BMN'
        verbose_name_plural = 'Detail Barang Penghapusan BMN'

    def __str__(self):
        return f'{self.nomor_urut}. {self.nama_barang}'
