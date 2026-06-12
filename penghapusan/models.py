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
        ('DRAFT', 'Draft'),
        ('DIAJUKAN', 'Diajukan Unit Kerja'),
        ('DIVERIFIKASI_BIRO', 'Diverifikasi Biro Umum'),
        ('PERLU_PERBAIKAN', 'Perlu Perbaikan Usulan'),
        ('DITOLAK', 'Ditolak'),
        ('DISETUJUI', 'Disetujui'),
        ('PROSES_PENGHAPUSAN', 'Proses Penghapusan'),
        ('SELESAI', 'Selesai/Dihapuskan'),
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

    status = models.CharField(max_length=30, choices=STATUS_PERMOHONAN, default='DIAJUKAN')
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
        if self.status in ['SELESAI', 'DITOLAK']:
            return 'success'
        if self.status == 'PERLU_PERBAIKAN':
            return 'warning' if self.lama_proses_hari <= 7 else 'danger'
        if self.status == 'DIAJUKAN':
            if self.lama_proses_hari >= 7:
                return 'danger'
            if self.lama_proses_hari >= 3:
                return 'warning'
            return 'success'
        if self.status in ['DIVERIFIKASI_BIRO', 'DISETUJUI', 'PROSES_PENGHAPUSAN']:
            if self.lama_proses_hari >= 14:
                return 'danger'
            if self.lama_proses_hari >= 7:
                return 'warning'
            return 'success'
        return 'success'

    @property
    def status_pengingat_label(self):
        if self.status in ['SELESAI', 'DITOLAK']:
            return 'Selesai'
        if self.status == 'PERLU_PERBAIKAN':
            return 'Menunggu perbaikan Satker'
        if self.status == 'DIAJUKAN':
            if self.lama_proses_hari >= 7:
                return 'Terlambat diverifikasi'
            if self.lama_proses_hari >= 3:
                return 'Perlu segera diverifikasi'
            return 'Menunggu verifikasi Biro Umum'
        if self.status in ['DIVERIFIKASI_BIRO', 'DISETUJUI', 'PROSES_PENGHAPUSAN']:
            if self.lama_proses_hari >= 14:
                return 'Proses melewati batas pantau'
            if self.lama_proses_hari >= 7:
                return 'Perlu tindak lanjut'
            return 'Dalam proses Biro Umum'
        return 'Dalam proses'

    @property
    def pesan_pengingat_pemohon(self):
        if self.status == 'PERLU_PERBAIKAN':
            return 'Pemohon/Satker perlu segera memperbaiki atau melengkapi usulan sesuai catatan Biro Umum.'
        if self.status == 'DIAJUKAN':
            return 'Usulan sudah dikirim ke Biro Umum. Pantau status dan lengkapi dokumen bila diminta.'
        return ''

    @property
    def pesan_pengingat_verifikator(self):
        if self.status == 'DIAJUKAN' and self.lama_proses_hari >= 3:
            return 'Pengingat untuk Biro Umum: permohonan sudah menunggu verifikasi beberapa hari.'
        if self.status in ['DIVERIFIKASI_BIRO', 'DISETUJUI', 'PROSES_PENGHAPUSAN'] and self.lama_proses_hari >= 7:
            return 'Pengingat untuk Biro Umum: permohonan perlu tindak lanjut proses/persetujuan/SK/BA.'
        return ''

    def save(self, *args, **kwargs):
        if not self.nomor_permohonan:
            super().save(*args, **kwargs)
            self.nomor_permohonan = f'UP-BMN/{self.tanggal_permohonan:%Y}/{self.pk:05d}'
            kwargs['force_insert'] = False
            kwargs['force_update'] = True
        super().save(*args, **kwargs)
