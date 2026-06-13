from django.conf import settings
from django.db import models
from master.models import TimeStampedModel, UnitKerja


class TanahNegara(TimeStampedModel):
    STATUS_TANAH = [
        ('DIGUNAKAN', 'Digunakan'),
        ('IDLE', 'Idle'),
        ('SENGKETA', 'Sengketa dengan Warga'),
        ('DISEWAKAN', 'Disewakan/Dimanfaatkan'),
        ('LAINNYA', 'Lainnya'),
    ]

    kode_tanah = models.CharField(max_length=80, unique=True)
    kode_satker = models.CharField(max_length=120, blank=True, null=True)
    nama_satker = models.CharField(max_length=200, blank=True, null=True)
    unit_kerja = models.ForeignKey(UnitKerja, on_delete=models.SET_NULL, null=True, blank=True, related_name='tanah_negara')

    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    nup = models.CharField(max_length=100, blank=True, null=True)
    nama_barang = models.CharField(max_length=220, blank=True, null=True)
    nama_aset = models.CharField(max_length=220, blank=True, null=True)
    nama_tanah = models.CharField(max_length=220)

    status_bmn = models.CharField(max_length=100, blank=True, null=True)
    kondisi = models.CharField(max_length=100, blank=True, null=True)
    intra_extra = models.CharField(max_length=50, blank=True, null=True)

    jenis_dokumen = models.CharField(max_length=255, blank=True, null=True)
    nomor_dokumen = models.CharField(max_length=180, blank=True, null=True)
    status_sertifikasi = models.CharField(max_length=180, blank=True, null=True)
    jenis_sertipikat = models.CharField(max_length=180, blank=True, null=True)
    nomor_sertifikat = models.CharField(max_length=180, blank=True, null=True)
    atas_nama_sertifikat = models.CharField(max_length=220, blank=True, null=True)
    tanggal_sertifikat = models.DateField(blank=True, null=True)
    tanggal_buku_pertama = models.DateField(blank=True, null=True)
    tanggal_perolehan = models.DateField(blank=True, null=True)

    nilai_perolehan = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    nilai_buku = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    luas_tanah = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    luas_tanah_seluruhnya = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    luas_tanah_untuk_bangunan = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    luas_tanah_untuk_sarana_lingkungan = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    luas_lahan_kosong = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    luas_pemanfaatan = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    jumlah_foto = models.PositiveIntegerField(default=0)

    status_penggunaan = models.CharField(max_length=255, blank=True, null=True)
    status_pemanfaatan = models.CharField(max_length=255, blank=True, null=True)
    status_tanah = models.CharField(max_length=30, choices=STATUS_TANAH, default='DIGUNAKAN')
    no_psp = models.CharField(max_length=180, blank=True, null=True)
    tanggal_psp = models.DateField(blank=True, null=True)

    alamat = models.TextField(blank=True, null=True)
    rt_rw = models.CharField(max_length=80, blank=True, null=True)
    kelurahan_desa = models.CharField(max_length=120, blank=True, null=True)
    kelurahan = models.CharField(max_length=120, blank=True, null=True)
    kecamatan = models.CharField(max_length=120, blank=True, null=True)
    kab_kota = models.CharField(max_length=150, blank=True, null=True)
    kabupaten_kota = models.CharField(max_length=150, blank=True, null=True)
    kode_kab_kota = models.CharField(max_length=80, blank=True, null=True)
    provinsi = models.CharField(max_length=120, blank=True, null=True)
    kode_provinsi = models.CharField(max_length=80, blank=True, null=True)
    kode_pos = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)

    sbsk = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    optimalisasi = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    penghuni = models.CharField(max_length=220, blank=True, null=True)
    pengguna = models.CharField(max_length=220, blank=True, null=True)
    digunakan_oleh = models.CharField(max_length=220, blank=True, null=True)

    kode_kpknl = models.CharField(max_length=80, blank=True, null=True)
    uraian_kpknl = models.CharField(max_length=180, blank=True, null=True)
    uraian_kanwil_djkn = models.CharField(max_length=180, blank=True, null=True)
    nama_kl = models.CharField(max_length=180, blank=True, null=True)
    nama_e1 = models.CharField(max_length=180, blank=True, null=True)
    nama_korwil = models.CharField(max_length=180, blank=True, null=True)
    kode_register = models.CharField(max_length=180, blank=True, null=True)
    status_pmk = models.CharField(max_length=180, blank=True, null=True)

    keterangan = models.TextField(blank=True, null=True)
    dokumen_sertifikat = models.FileField(upload_to='tanah_negara/sertifikat/', blank=True, null=True)
    dibuat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['kode_tanah']
        verbose_name = 'Tanah Negara'
        verbose_name_plural = 'Tanah Negara'

    @property
    def is_pdf(self):
        return bool(self.dokumen_sertifikat and self.dokumen_sertifikat.name.lower().endswith('.pdf'))

    def __str__(self):
        return f'{self.kode_tanah} - {self.nama_tanah}'
