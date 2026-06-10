from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from core.constants import KONDISI_ASET, STATUS_SIP, JENIS_KENDARAAN_CHOICES
from master.models import Kendaraan, Pegawai, TimeStampedModel

class SIPKendaraan(TimeStampedModel):
    nomor_sip = models.CharField(max_length=100, unique=True)
    tanggal_sip = models.DateField()
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.CASCADE, related_name='sip_kendaraan')
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='sip_kendaraan')
    tanggal_mulai = models.DateField()
    tanggal_akhir = models.DateField()
    jenis_pemakaian = models.CharField('Jenis Kendaraan', max_length=30, choices=JENIS_KENDARAAN_CHOICES, blank=True, null=True)
    tujuan_pemakaian = models.TextField(blank=True, null=True)
    lokasi_penggunaan = models.CharField(max_length=200, blank=True, null=True)
    dasar_penerbitan = models.TextField(blank=True, null=True)
    pejabat_penandatangan = models.CharField(max_length=150, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_SIP, default='DRAFT')
    dokumen_sip = models.FileField(upload_to='sip_kendaraan/', blank=True, null=True)
    catatan = models.TextField(blank=True, null=True)
    dibuat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        ordering = ['-tanggal_sip']
    def clean(self):
        if self.tanggal_akhir and self.tanggal_mulai and self.tanggal_akhir < self.tanggal_mulai:
            raise ValidationError('Tanggal akhir tidak boleh lebih kecil dari tanggal mulai.')
        if self.status == 'AKTIF' and self.kendaraan_id and self.kendaraan.kondisi == 'RUSAK_BERAT':
            raise ValidationError('Kendaraan rusak berat tidak boleh memiliki SIP aktif.')
        if self.status == 'AKTIF' and self.kendaraan_id and self.tanggal_mulai and self.tanggal_akhir:
            qs = SIPKendaraan.objects.filter(kendaraan=self.kendaraan, status='AKTIF')
            if self.pk: qs = qs.exclude(pk=self.pk)
            if qs.filter(tanggal_mulai__lte=self.tanggal_akhir, tanggal_akhir__gte=self.tanggal_mulai).exists():
                raise ValidationError('Kendaraan sudah memiliki SIP aktif pada periode tersebut.')
    def __str__(self): return self.nomor_sip

class ServiceKendaraan(TimeStampedModel):
    JENIS_SERVICE = [
        ('SERVICE_BERKALA', 'Service Berkala'), ('GANTI_OLI', 'Ganti Oli'),
        ('GANTI_BAN', 'Ganti Ban'), ('GANTI_AKI', 'Ganti Aki'),
        ('PERBAIKAN_MESIN', 'Perbaikan Mesin'), ('PERBAIKAN_BODY', 'Perbaikan Body'),
        ('LAINNYA', 'Lainnya'),
    ]
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.CASCADE, related_name='service')
    tanggal_service = models.DateField()
    jenis_service = models.CharField(max_length=50, choices=JENIS_SERVICE)
    kilometer = models.PositiveIntegerField(blank=True, null=True)
    bengkel = models.CharField(max_length=150, blank=True, null=True)
    uraian_pekerjaan = models.TextField()
    sparepart_diganti = models.TextField(blank=True, null=True)
    biaya_jasa = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    biaya_sparepart = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_biaya = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    kondisi_sebelum = models.CharField(max_length=20, choices=KONDISI_ASET)
    kondisi_sesudah = models.CharField(max_length=20, choices=KONDISI_ASET)
    dokumen_bukti = models.FileField(upload_to='service_kendaraan/dokumen/', blank=True, null=True)
    foto_sebelum = models.ImageField(upload_to='service_kendaraan/sebelum/', blank=True, null=True)
    foto_sesudah = models.ImageField(upload_to='service_kendaraan/sesudah/', blank=True, null=True)
    dicatat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        ordering = ['-tanggal_service']
    def save(self, *args, **kwargs):
        self.total_biaya = (self.biaya_jasa or 0) + (self.biaya_sparepart or 0)
        super().save(*args, **kwargs)
        fields=[]
        if self.kendaraan.kondisi != self.kondisi_sesudah:
            self.kendaraan.kondisi = self.kondisi_sesudah; fields.append('kondisi')
        if self.kilometer is not None and self.kendaraan.kilometer_terakhir != self.kilometer:
            self.kendaraan.kilometer_terakhir = self.kilometer; fields.append('kilometer_terakhir')
        if fields:
            fields.append('updated_at'); self.kendaraan.save(update_fields=fields)
    def __str__(self): return f'{self.kendaraan} - {self.tanggal_service}'

class BuktiKuitansiServiceKendaraan(TimeStampedModel):
    service = models.ForeignKey(
        ServiceKendaraan,
        on_delete=models.CASCADE,
        related_name='bukti_kuitansi'
    )

    file = models.FileField(
        upload_to='service_kendaraan/kuitansi/'
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
        verbose_name = 'Bukti Kuitansi Service Kendaraan'
        verbose_name_plural = 'Bukti Kuitansi Service Kendaraan'

    @property
    def is_pdf(self):
        return bool(self.file and self.file.name.lower().endswith('.pdf'))

    def __str__(self):
        return f'Kuitansi {self.service.kendaraan} - {self.created_at:%d-%m-%Y}'

class RiwayatKondisiKendaraan(TimeStampedModel):
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.CASCADE, related_name='riwayat_kondisi')
    tanggal = models.DateField()
    kondisi = models.CharField(max_length=20, choices=KONDISI_ASET)
    uraian_kondisi = models.TextField(blank=True, null=True)
    foto_kondisi = models.ImageField(upload_to='kondisi_kendaraan/', blank=True, null=True)
    dicatat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        ordering = ['-tanggal']
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.kendaraan.kondisi != self.kondisi:
            self.kendaraan.kondisi = self.kondisi
            self.kendaraan.save(update_fields=['kondisi','updated_at'])
    def __str__(self): return f'{self.kendaraan} - {self.get_kondisi_display()}'
