from django.conf import settings
from django.db import models
from core.constants import KONDISI_ASET, STATUS_PEMANFAATAN_KENDARAAN, STATUS_PEMANFAATAN_RUMAH, JENIS_KENDARAAN_CHOICES

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class UnitKerja(TimeStampedModel):
    nama_unit = models.CharField(max_length=150, unique=True)
    keterangan = models.TextField(blank=True, null=True)
    class Meta:
        ordering = ['nama_unit']
    def __str__(self): return self.nama_unit

class Pegawai(TimeStampedModel):
    nip = models.CharField(max_length=30, unique=True)
    nik = models.CharField(max_length=30, blank=True, null=True)
    nama = models.CharField(max_length=150)
    jabatan = models.CharField(max_length=150, blank=True, null=True)
    pangkat = models.CharField(max_length=100, blank=True, null=True)
    golongan = models.CharField(max_length=20, blank=True, null=True)
    unit_kerja = models.ForeignKey(UnitKerja, on_delete=models.SET_NULL, null=True, blank=True, related_name='pegawai')
    no_hp = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    status_pegawai = models.CharField(max_length=50, default='Aktif')
    foto = models.ImageField(upload_to='pegawai/', blank=True, null=True)
    class Meta:
        ordering = ['nama']
    def __str__(self): return f'{self.nama} - {self.nip}'

class Kendaraan(TimeStampedModel):
    kode_kendaraan = models.CharField(max_length=50, unique=True)
    nomor_polisi = models.CharField(max_length=30, unique=True)
    merek = models.CharField(max_length=100)
    tipe = models.CharField(max_length=100, blank=True, null=True)
    jenis_kendaraan = models.CharField(max_length=30, choices=JENIS_KENDARAAN_CHOICES, blank=True, null=True)
    tahun_pembuatan = models.PositiveIntegerField(blank=True, null=True)
    tahun_perolehan = models.PositiveIntegerField(blank=True, null=True)
    warna = models.CharField(max_length=50, blank=True, null=True)
    nomor_rangka = models.CharField(max_length=100, blank=True, null=True)
    nomor_mesin = models.CharField(max_length=100, blank=True, null=True)
    nomor_bpkb = models.CharField(max_length=100, blank=True, null=True)
    nomor_stnk = models.CharField(max_length=100, blank=True, null=True)
    masa_berlaku_stnk = models.DateField(blank=True, null=True)
    jatuh_tempo_pajak = models.DateField(blank=True, null=True)
    nup = models.CharField(max_length=100, blank=True, null=True)
    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    nilai_perolehan = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    unit_kerja = models.ForeignKey(UnitKerja, on_delete=models.SET_NULL, null=True, blank=True, related_name='kendaraan')
    pengguna = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='kendaraan_digunakan')
    kondisi = models.CharField(max_length=20, choices=KONDISI_ASET, default='BAIK')
    status_pemanfaatan = models.CharField(max_length=30, choices=STATUS_PEMANFAATAN_KENDARAAN, default='TERSEDIA')
    kilometer_terakhir = models.PositiveIntegerField(default=0)
    foto = models.ImageField(upload_to='kendaraan/', blank=True, null=True)
    dokumen_stnk = models.FileField(upload_to='kendaraan/dokumen/stnk/', blank=True, null=True)
    dokumen_bpkb = models.FileField(upload_to='kendaraan/dokumen/bpkb/', blank=True, null=True)
    class Meta:
        ordering = ['nomor_polisi']
    def __str__(self): return f'{self.nomor_polisi} - {self.merek}'


class FotoKendaraan(TimeStampedModel):
    kendaraan = models.ForeignKey(
        Kendaraan,
        on_delete=models.CASCADE,
        related_name='galeri_foto'
    )
    foto = models.ImageField(upload_to='kendaraan/galeri/')
    keterangan = models.CharField(max_length=200, blank=True, null=True)
    diupload_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Foto {self.kendaraan.nomor_polisi}'


class RumahDinas(TimeStampedModel):
    kode_rumah = models.CharField(max_length=50, unique=True)
    nama_rumah = models.CharField(max_length=150)
    jenis_rumah = models.CharField(max_length=100, blank=True, null=True)
    alamat = models.TextField()
    provinsi = models.CharField(max_length=100, blank=True, null=True)
    kabupaten_kota = models.CharField(max_length=100, blank=True, null=True)
    kecamatan = models.CharField(max_length=100, blank=True, null=True)
    kelurahan = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    luas_tanah = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    luas_bangunan = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    jumlah_kamar_tidur = models.PositiveIntegerField(default=0)
    jumlah_kamar_mandi = models.PositiveIntegerField(default=0)
    daya_listrik = models.CharField(max_length=50, blank=True, null=True)
    tahun_dibangun = models.PositiveIntegerField(blank=True, null=True)
    tahun_perolehan = models.PositiveIntegerField(blank=True, null=True)
    nup = models.CharField(max_length=100, blank=True, null=True)
    kode_barang = models.CharField(max_length=100, blank=True, null=True)
    nilai_perolehan = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    unit_kerja = models.ForeignKey(UnitKerja, on_delete=models.SET_NULL, null=True, blank=True, related_name='rumah_negara')
    nomor_sertifikat = models.CharField(max_length=100, blank=True, null=True)
    status_tanah = models.CharField(max_length=100, blank=True, null=True)
    kondisi = models.CharField(max_length=20, choices=KONDISI_ASET, default='BAIK')
    status_pemanfaatan = models.CharField(max_length=30, choices=STATUS_PEMANFAATAN_RUMAH, default='KOSONG')
    foto_depan = models.ImageField(upload_to='rumah_dinas/', blank=True, null=True)
    class Meta:
        ordering = ['kode_rumah']
    def __str__(self): return f'{self.kode_rumah} - {self.nama_rumah}'


class FotoRumahDinas(TimeStampedModel):
    rumah_dinas = models.ForeignKey(
        RumahDinas,
        on_delete=models.CASCADE,
        related_name='galeri_foto'
    )

    foto = models.ImageField(
        upload_to='rumah_dinas/galeri/'
    )

    keterangan = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    diupload_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Foto Rumah Dinas'
        verbose_name_plural = 'Foto Rumah Dinas'

    def __str__(self):
        return f'Foto {self.rumah_dinas.kode_rumah}'
