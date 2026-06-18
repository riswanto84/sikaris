import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from core.constants import KONDISI_ASET, STATUS_SIP, JENIS_KENDARAAN_CHOICES
from core.models import next_nomor_surat
from master.models import Kendaraan, Pegawai, TimeStampedModel


def get_pegawai_by_jabatan(jabatan_keyword, fallback):
    try:
        pegawai = (
            Pegawai.objects
            .filter(jabatan__icontains=jabatan_keyword, status_pegawai__iexact='Aktif')
            .order_by('nama')
            .first()
        ) or (
            Pegawai.objects
            .filter(jabatan__icontains=jabatan_keyword)
            .order_by('nama')
            .first()
        )
        if pegawai:
            return f'{pegawai.nama} - {pegawai.jabatan or jabatan_keyword}'
    except Exception:
        pass
    return fallback

class SIPKendaraan(TimeStampedModel):
    nomor_sip = models.CharField(max_length=100, unique=True, blank=True, help_text="Otomatis dari sistem jika dikosongkan. Format: nomor/1/PL.02/SIKARIS/bulan/tahun, contoh 2/1/PL.02/SIKARIS/01/2025")
    tanggal_sip = models.DateField()
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.CASCADE, related_name='sip_kendaraan')
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='sip_kendaraan')
    tanggal_mulai = models.DateField()
    tanggal_akhir = models.DateField()
    jenis_pemakaian = models.CharField('Jenis Kendaraan', max_length=100, choices=JENIS_KENDARAAN_CHOICES, blank=True, null=True)
    tujuan_pemakaian = models.TextField(blank=True, null=True)
    lokasi_penggunaan = models.CharField(max_length=200, blank=True, null=True)
    dasar_penerbitan = models.TextField(blank=True, null=True)
    pejabat_penandatangan = models.CharField(max_length=150, blank=True, null=True)
    pejabat_penerbit_sip_kendaraan = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_kendaraan_diterbitkan')
    nama_pejabat_penerbit_sip_kendaraan = models.CharField(max_length=150, blank=True, null=True)
    nip_pejabat_penerbit_sip_kendaraan = models.CharField(max_length=30, blank=True, null=True)
    jabatan_pejabat_penerbit_sip_kendaraan = models.CharField(max_length=180, blank=True, null=True)
    status_tte = models.CharField(max_length=20, choices=[('BELUM', 'Belum TTE'), ('SIAP_TTE', 'Siap TTE'), ('PROSES_TTE', 'Proses TTE'), ('SUDAH_TTE', 'Sudah TTE'), ('DITOLAK_TTE', 'Ditolak TTE')], default='BELUM')
    tanggal_tte = models.DateTimeField(blank=True, null=True)
    catatan_tte = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS_SIP, default='DRAFT')
    masa_berlaku_sip = models.CharField(max_length=150, blank=True, null=True)
    dokumen_sip = models.FileField(upload_to='sip_kendaraan/', blank=True, null=True)
    dokumen_lainnya = models.FileField('Dokumen Lainnya / Lampiran Pendukung (Opsional)', upload_to='sip_kendaraan/lampiran_lainnya/', blank=True, null=True, help_text='Opsional. Upload lampiran pendukung seperti surat tugas, nota dinas, identitas, atau dokumen lain yang diperlukan.')
    file_konsep_pdf = models.FileField(upload_to='sip_kendaraan/konsep/', blank=True, null=True)
    file_tte_pengusul = models.FileField(upload_to='sip_kendaraan/tte_pengusul/', blank=True, null=True)
    status_tte_pengusul = models.CharField(max_length=20, choices=[('BELUM', 'Belum TTE Pengusul'), ('SUDAH_TTE', 'Sudah TTE Pengusul')], default='BELUM')
    tanggal_tte_pengusul = models.DateTimeField(blank=True, null=True)
    catatan_tte_pengusul = models.TextField(blank=True, null=True)
    file_final_pdf = models.FileField(upload_to='sip_kendaraan/final/', blank=True, null=True)
    file_signed_pdf = models.FileField(upload_to='sip_kendaraan/signed/', blank=True, null=True)
    tanggal_pengajuan = models.DateTimeField(blank=True, null=True)
    tanggal_persetujuan = models.DateTimeField(blank=True, null=True)
    disetujui_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_kendaraan_disetujui')
    catatan_penolakan = models.TextField(blank=True, null=True)
    catatan = models.TextField(blank=True, null=True)
    dibuat_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        ordering = ['-tanggal_sip']
    def clean(self):
        if self.tanggal_akhir and self.tanggal_mulai and self.tanggal_akhir < self.tanggal_mulai:
            raise ValidationError('Tanggal akhir tidak boleh lebih kecil dari tanggal mulai.')
        if self.status in ['TERBIT', 'DISETUJUI', 'AKTIF'] and self.kendaraan_id and self.kendaraan.kondisi == 'RUSAK_BERAT':
            raise ValidationError('Kendaraan rusak berat tidak boleh memiliki SIP aktif.')
        if self.status in ['TERBIT', 'DISETUJUI', 'AKTIF'] and self.kendaraan_id and self.tanggal_mulai and self.tanggal_akhir:
            qs = SIPKendaraan.objects.filter(kendaraan=self.kendaraan, status__in=['TERBIT', 'DISETUJUI', 'AKTIF'])
            if self.pk: qs = qs.exclude(pk=self.pk)
            if qs.filter(tanggal_mulai__lte=self.tanggal_akhir, tanggal_akhir__gte=self.tanggal_mulai).exists():
                raise ValidationError('Kendaraan sudah memiliki SIP aktif pada periode tersebut.')
    @property
    def status_aktif_display(self):
        return 'Aktif' if self.status in ['TERBIT', 'AKTIF'] else 'Non Aktif'

    @property
    def masa_berlaku_display(self):
        if self.masa_berlaku_sip:
            return self.masa_berlaku_sip
        if self.tanggal_mulai and self.tanggal_akhir:
            return f'{self.tanggal_mulai:%d/%m/%Y} s.d. {self.tanggal_akhir:%d/%m/%Y}'
        return '-'

    def _last_nomor_urut_tahun(self):
        tahun = self.tanggal_sip.year if self.tanggal_sip else None
        if not tahun:
            return 0
        qs = SIPKendaraan.objects.filter(tanggal_sip__year=tahun)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        last = 0
        for nomor in qs.values_list('nomor_sip', flat=True):
            match = re.match(r'^(\d+)/', str(nomor or '').strip())
            if match:
                last = max(last, int(match.group(1)))
        return last

    def save(self, *args, **kwargs):
        if not self.nomor_sip:
            self.nomor_sip = next_nomor_surat(
                'SIP_KENDARAAN',
                self.tanggal_sip,
                kode_unit='1',
                kode_klasifikasi='PL.02',
                start=self._last_nomor_urut_tahun() + 1,
            )
        from .sip_penerbit import apply_snapshot_penerbit_sip_kendaraan
        apply_snapshot_penerbit_sip_kendaraan(self)
        super().save(*args, **kwargs)

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
