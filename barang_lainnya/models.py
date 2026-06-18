from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from master.models import Pegawai, TimeStampedModel


STATUS_SIP_BARANG = [
    ('DRAFT', 'Draft/Konsep'),
    ('DIAJUKAN', 'Diajukan'),
    ('DITOLAK', 'Ditolak'),
    ('TERBIT', 'Terbit'),
]


class SIPBarangLainnya(TimeStampedModel):
    nomor_sip = models.CharField(max_length=100, unique=True, help_text="Nomor SIP diinput manual oleh pengguna.")
    tanggal_sip = models.DateField(default=timezone.now)
    pemegang_sip = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='sip_barang_lainnya_pemegang')
    pengguna_aktual = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_barang_lainnya_pengguna')
    tanggal_mulai = models.DateField()
    tanggal_akhir = models.DateField()
    dasar_penerbitan = models.TextField(blank=True, null=True)
    tujuan_penggunaan = models.TextField(blank=True, null=True)
    lokasi_penggunaan = models.CharField(max_length=255, blank=True, null=True)
    pejabat_penandatangan = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_barang_lainnya_penandatangan')
    nama_pejabat_penandatangan = models.CharField(max_length=150, blank=True, null=True)
    nip_pejabat_penandatangan = models.CharField(max_length=30, blank=True, null=True)
    jabatan_pejabat_penandatangan = models.CharField(max_length=180, blank=True, null=True)
    keterangan_tambahan = models.TextField(blank=True, null=True)
    dokumen_pendukung = models.FileField(upload_to='sip_barang_lainnya/lampiran/', blank=True, null=True)
    file_konsep_pdf = models.FileField(upload_to='sip_barang_lainnya/konsep/', blank=True, null=True)
    file_signed_pdf = models.FileField(upload_to='sip_barang_lainnya/signed/', blank=True, null=True)
    status_tte = models.CharField(max_length=20, choices=[('BELUM', 'Belum TTE'), ('SUDAH_TTE', 'Sudah TTE')], default='BELUM')
    tanggal_tte = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_SIP_BARANG, default='DRAFT')
    tanggal_pengajuan = models.DateTimeField(blank=True, null=True)
    tanggal_persetujuan = models.DateTimeField(blank=True, null=True)
    disetujui_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_barang_lainnya_disetujui')
    catatan = models.TextField(blank=True, null=True)
    catatan_penolakan = models.TextField(blank=True, null=True)
    dibuat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_barang_lainnya_dibuat')

    class Meta:
        ordering = ['-tanggal_sip', '-created_at']
        verbose_name = 'SIP Barang Lainnya'
        verbose_name_plural = 'SIP Barang Lainnya'

    def __str__(self):
        return self.nomor_sip or f'SIP Barang Lainnya #{self.pk}'

    def clean(self):
        if self.tanggal_mulai and self.tanggal_akhir and self.tanggal_akhir < self.tanggal_mulai:
            raise ValidationError('Tanggal akhir tidak boleh lebih kecil dari tanggal mulai.')

    @property
    def status_aktif_display(self):
        return 'Aktif' if self.status == 'TERBIT' else 'Non Aktif'

    @property
    def masa_berlaku_display(self):
        if self.tanggal_mulai and self.tanggal_akhir:
            return f'{self.tanggal_mulai:%d %b %Y} s.d. {self.tanggal_akhir:%d %b %Y}'
        return '-'

    def save(self, *args, **kwargs):
        if self.pejabat_penandatangan:
            self.nama_pejabat_penandatangan = self.pejabat_penandatangan.nama
            self.nip_pejabat_penandatangan = self.pejabat_penandatangan.nip
            self.jabatan_pejabat_penandatangan = self.pejabat_penandatangan.jabatan
        if self.file_signed_pdf and self.status_tte != 'SUDAH_TTE':
            self.status_tte = 'SUDAH_TTE'
            self.tanggal_tte = self.tanggal_tte or timezone.now()
        super().save(*args, **kwargs)


class SIPBarangLainnyaItem(TimeStampedModel):
    sip = models.ForeignKey(SIPBarangLainnya, on_delete=models.CASCADE, related_name='items')
    urutan = models.PositiveIntegerField(default=1)
    nama_barang = models.CharField(max_length=200)
    spesifikasi = models.CharField(max_length=255, blank=True, null=True)
    satuan = models.CharField(max_length=50, default='Unit')
    jumlah = models.PositiveIntegerField(default=1)
    nup = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=150, blank=True, null=True)
    keterangan = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['urutan', 'id']
        verbose_name = 'Item SIP Barang Lainnya'
        verbose_name_plural = 'Item SIP Barang Lainnya'

    def __str__(self):
        return f'{self.nama_barang} ({self.sip.nomor_sip})'
