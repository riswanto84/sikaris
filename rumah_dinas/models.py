from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from core.constants import STATUS_SIP
from master.models import RumahDinas, Pegawai, TimeStampedModel

class SIPRumahDinas(TimeStampedModel):
    STATUS_SIP_RUMAH = STATUS_SIP + [('PENGOSONGAN','Dalam Proses Pengosongan')]
    nomor_sip = models.CharField(max_length=100, unique=True)
    tanggal_sip = models.DateField()
    rumah_dinas = models.ForeignKey(RumahDinas, on_delete=models.CASCADE, related_name='sip_rumah')
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='sip_rumah', verbose_name='Pemegang SIP')
    penghuni = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_rumah_dihuni', verbose_name='Penghuni Aktual')
    STATUS_BAYAR_PNBP = [('SUDAH_BAYAR','Sudah Bayar'), ('BELUM_BAYAR','Belum Bayar'), ('TIDAK_WAJIB','Tidak Wajib')]
    tanggal_mulai = models.DateField()
    tanggal_akhir = models.DateField()
    dasar_penerbitan = models.TextField(blank=True, null=True)
    pejabat_penandatangan = models.CharField(max_length=150, blank=True, null=True)
    jumlah_anggota_keluarga = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_SIP_RUMAH, default='DRAFT')
    dokumen_sip = models.FileField(upload_to='sip_rumah_dinas/', blank=True, null=True)
    dokumen_bast = models.FileField(upload_to='bast_rumah_dinas/', blank=True, null=True)
    status_bayar_pnbp = models.CharField(max_length=20, choices=STATUS_BAYAR_PNBP, default='BELUM_BAYAR')
    tahun_pnbp = models.PositiveIntegerField(blank=True, null=True)
    nilai_pnbp = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tanggal_bayar_pnbp = models.DateField(blank=True, null=True)
    bukti_bayar_pnbp = models.FileField(upload_to='pnbp_rumah_negara/', blank=True, null=True)
    catatan = models.TextField(blank=True, null=True)
    dibuat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        ordering=['-tanggal_sip']
    def clean(self):
        if self.tanggal_akhir and self.tanggal_mulai and self.tanggal_akhir < self.tanggal_mulai:
            raise ValidationError('Tanggal akhir tidak boleh lebih kecil dari tanggal mulai.')
        if self.status == 'AKTIF' and self.rumah_dinas_id and self.rumah_dinas.kondisi == 'RUSAK_BERAT':
            raise ValidationError('Rumah negara rusak berat tidak boleh memiliki SIP aktif.')
        if self.status == 'AKTIF' and self.rumah_dinas_id and self.tanggal_mulai and self.tanggal_akhir:
            qs = SIPRumahDinas.objects.filter(rumah_dinas=self.rumah_dinas, status='AKTIF')
            if self.pk: qs = qs.exclude(pk=self.pk)
            if qs.filter(tanggal_mulai__lte=self.tanggal_akhir, tanggal_akhir__gte=self.tanggal_mulai).exists():
                raise ValidationError('Rumah negara sudah memiliki SIP aktif pada periode tersebut.')
    def __str__(self): return self.nomor_sip

class PerbaikanRumahDinas(TimeStampedModel):
    rumah_dinas = models.ForeignKey(RumahDinas, on_delete=models.CASCADE, related_name='perbaikan')
    pelapor = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True)
    tanggal_laporan = models.DateField()
    jenis_kerusakan = models.CharField(max_length=100)
    uraian_kerusakan = models.TextField()
    estimasi_biaya = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    realisasi_biaya = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default='Dilaporkan')
    foto_sebelum = models.ImageField(upload_to='perbaikan_rumah/sebelum/', blank=True, null=True)
    foto_sesudah = models.ImageField(upload_to='perbaikan_rumah/sesudah/', blank=True, null=True)
    def __str__(self): return f'{self.rumah_dinas} - {self.jenis_kerusakan}'
