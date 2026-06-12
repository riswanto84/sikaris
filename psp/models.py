from django.conf import settings
from django.db import models
from django.utils import timezone

from master.models import Kendaraan, Pegawai, RumahDinas, TimeStampedModel, UnitKerja


class PermohonanPSPBMN(TimeStampedModel):
    JENIS_BARANG = [
        ('KENDARAAN', 'Kendaraan'),
        ('RUMAH_NEGARA', 'Rumah Negara'),
        ('TANAH_NEGARA', 'Tanah Negara'),
        ('LAINNYA', 'BMN Lainnya'),
    ]

    STATUS_PERMOHONAN = [
        ('DRAFT', 'Draft'),
        ('DIAJUKAN', 'Diajukan Unit Kerja'),
        ('DIVERIFIKASI_BIRO', 'Diverifikasi Biro Umum'),
        ('PERLU_PERBAIKAN', 'Perlu Perbaikan Usulan'),
        ('DITOLAK', 'Ditolak'),
        ('DISETUJUI', 'Disetujui/Penetapan PSP'),
        ('SELESAI', 'Selesai'),
    ]

    nomor_permohonan = models.CharField(max_length=120, unique=True, blank=True)
    tanggal_permohonan = models.DateField(default=timezone.now)
    unit_kerja = models.ForeignKey(UnitKerja, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')
    pemohon = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')

    jenis_barang = models.CharField(max_length=30, choices=JENIS_BARANG)
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')
    rumah_negara = models.ForeignKey(RumahDinas, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')
    tanah_negara = models.ForeignKey('tanah_negara.TanahNegara', on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp')

    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    nup = models.CharField(max_length=100, blank=True, null=True)
    nama_barang = models.CharField(max_length=220)
    nilai_psp = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    kondisi_barang = models.CharField(max_length=120, blank=True, null=True)
    lokasi_barang = models.TextField(blank=True, null=True)
    keterangan_barang = models.TextField(blank=True, null=True)

    # Dokumen dasar PSP sampai dengan Rp100 juta dan tetap wajib untuk seluruh usulan.
    surat_permohonan_satker = models.FileField(upload_to='psp/surat_permohonan_satker/', blank=True, null=True)
    surat_pengantar_eselon1 = models.FileField(upload_to='psp/surat_pengantar_eselon1/', blank=True, null=True)
    daftar_kondisi_barang = models.FileField(upload_to='psp/daftar_kondisi_barang/', blank=True, null=True)
    laporan_sub_kelompok_barang = models.FileField(upload_to='psp/laporan_sub_kelompok_barang/', blank=True, null=True)
    surat_pernyataan_kepala_satker = models.FileField(upload_to='psp/surat_pernyataan_kepala_satker/', blank=True, null=True)

    # Dokumen tambahan jika jenis barang kendaraan dan nilai PSP > Rp100 juta.
    foto_kendaraan = models.FileField(upload_to='psp/foto_kendaraan/', blank=True, null=True)
    dokumen_kepemilikan = models.FileField(upload_to='psp/dokumen_kepemilikan/', blank=True, null=True)
    surat_pernyataan_pengganti_kepemilikan = models.FileField(upload_to='psp/surat_pernyataan_pengganti_kepemilikan/', blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_PERMOHONAN, default='DIAJUKAN')
    catatan_unit = models.TextField(blank=True, null=True)
    catatan_biro_umum = models.TextField(blank=True, null=True)

    diverifikasi_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifikasi_psp')
    tanggal_verifikasi = models.DateField(blank=True, null=True)
    nomor_penetapan_psp = models.CharField(max_length=150, blank=True, null=True)
    tanggal_penetapan_psp = models.DateField(blank=True, null=True)
    dokumen_penetapan_psp = models.FileField(upload_to='psp/penetapan_psp/', blank=True, null=True)

    dibuat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp_dibuat')
    diperbarui_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permohonan_psp_diperbarui')

    class Meta:
        ordering = ['-tanggal_permohonan', '-created_at']
        verbose_name = 'Permohonan PSP BMN'
        verbose_name_plural = 'Permohonan PSP BMN'

    def __str__(self):
        return f'{self.nomor_permohonan or "Permohonan PSP"} - {self.nama_barang}'

    @property
    def is_kendaraan_diatas_100jt(self):
        try:
            return self.jenis_barang == 'KENDARAAN' and self.nilai_psp and self.nilai_psp > 100000000
        except Exception:
            return False

    @property
    def kategori_nilai_display(self):
        if self.is_kendaraan_diatas_100jt:
            return 'Kendaraan di atas Rp100 juta'
        return 'Dokumen dasar PSP'

    def save(self, *args, **kwargs):
        if not self.nomor_permohonan:
            super().save(*args, **kwargs)
            self.nomor_permohonan = f'PSP-BMN/{self.tanggal_permohonan:%Y}/{self.pk:05d}'
            kwargs['force_insert'] = False
            kwargs['force_update'] = True
        super().save(*args, **kwargs)
