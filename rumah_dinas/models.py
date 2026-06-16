import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from core.constants import STATUS_SIP
from core.models import next_nomor_surat
from master.models import RumahDinas, Pegawai, TimeStampedModel


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
            return f'{pegawai.nama} - {pegawai.jabatan or jabatan_keyword} (TTE BSrE)'
    except Exception:
        pass
    return fallback

class SIPRumahDinas(TimeStampedModel):
    STATUS_SIP_RUMAH = STATUS_SIP + [('PENGOSONGAN','Dalam Proses Pengosongan')]
    nomor_sip = models.CharField(max_length=100, unique=True, blank=True, help_text="Otomatis dari sistem jika dikosongkan. Format: nomor/1.5/PL.03/SIKARIS/bulan/tahun, contoh 1/1.5/PL.03/SIKARIS/01/2026")
    tanggal_sip = models.DateField()
    rumah_dinas = models.ForeignKey(RumahDinas, on_delete=models.CASCADE, related_name='sip_rumah')
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='sip_rumah', verbose_name='Pemegang SIP')
    penghuni = models.ForeignKey(Pegawai, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_rumah_dihuni', verbose_name='Penghuni Aktual')
    STATUS_BAYAR_PNBP = [('SUDAH_BAYAR','Sudah Bayar'), ('BELUM_BAYAR','Belum Bayar'), ('TIDAK_WAJIB','Tidak Wajib')]
    JENIS_MASA_BERLAKU = [
        ('TANGGAL', 'Berdasarkan Tanggal'),
        ('JABATAN', 'Selama Masih Menduduki Jabatan'),
    ]
    tanggal_mulai = models.DateField()
    tanggal_akhir = models.DateField()
    jenis_masa_berlaku = models.CharField(max_length=20, choices=JENIS_MASA_BERLAKU, default='JABATAN')
    masa_berlaku_sip = models.CharField(max_length=150, blank=True, null=True)
    dasar_penerbitan = models.TextField(blank=True, null=True)
    pejabat_penandatangan = models.CharField(max_length=150, blank=True, null=True)
    jumlah_anggota_keluarga = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=25, choices=STATUS_SIP_RUMAH, default='DRAFT')
    dokumen_sip = models.FileField(upload_to='sip_rumah_dinas/', blank=True, null=True)
    dokumen_lainnya = models.FileField('Dokumen Lainnya / Lampiran Pendukung (Opsional)', upload_to='sip_rumah_dinas/lampiran_lainnya/', blank=True, null=True, help_text='Opsional. Upload lampiran pendukung seperti surat pernyataan, identitas, dokumen keluarga, atau dokumen lain yang diperlukan.')
    file_konsep_pdf = models.FileField(upload_to='sip_rumah_dinas/konsep/', blank=True, null=True)
    file_tte_calon_pengguna = models.FileField(upload_to='sip_rumah_dinas/tte_calon_pengguna/', blank=True, null=True)
    status_tte_calon_pengguna = models.CharField(max_length=20, choices=[('BELUM', 'Belum TTE Calon Pengguna'), ('SUDAH_TTE', 'Sudah TTE Calon Pengguna')], default='BELUM')
    tanggal_tte_calon_pengguna = models.DateTimeField(blank=True, null=True)
    catatan_tte_calon_pengguna = models.TextField(blank=True, null=True)
    file_final_pdf = models.FileField(upload_to='sip_rumah_dinas/final/', blank=True, null=True)
    file_signed_pdf = models.FileField(upload_to='sip_rumah_dinas/signed/', blank=True, null=True)
    status_tte = models.CharField(max_length=20, choices=[('BELUM', 'Belum TTE'), ('SIAP_TTE', 'Siap TTE'), ('PROSES_TTE', 'Proses TTE'), ('SUDAH_TTE', 'Sudah TTE'), ('DITOLAK_TTE', 'Ditolak TTE')], default='BELUM')
    tanggal_tte = models.DateTimeField(blank=True, null=True)
    catatan_tte = models.TextField(blank=True, null=True)
    tanggal_pengajuan = models.DateTimeField(blank=True, null=True)
    tanggal_persetujuan = models.DateTimeField(blank=True, null=True)
    disetujui_oleh = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sip_rumah_disetujui')
    catatan_penolakan = models.TextField(blank=True, null=True)
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
    @property
    def masa_berlaku_display(self):
        if self.masa_berlaku_sip:
            return self.masa_berlaku_sip
        if self.jenis_masa_berlaku == 'JABATAN':
            return 'Selama masih menduduki jabatan'
        if self.tanggal_mulai and self.tanggal_akhir:
            return f'{self.tanggal_mulai:%d/%m/%Y} s.d. {self.tanggal_akhir:%d/%m/%Y}'
        return '-'

    def _last_nomor_urut_tahun(self):
        tahun = self.tanggal_sip.year if self.tanggal_sip else None
        if not tahun:
            return 0
        qs = SIPRumahDinas.objects.filter(tanggal_sip__year=tahun)
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
                'SIP_RUMAH_DINAS',
                self.tanggal_sip,
                kode_unit='1.5',
                kode_klasifikasi='PL.03',
                start=self._last_nomor_urut_tahun() + 1,
            )
        if not self.pejabat_penandatangan:
            self.pejabat_penandatangan = get_pegawai_by_jabatan('Sekretaris Jenderal', 'Sekretaris Jenderal (TTE BSrE)')
        super().save(*args, **kwargs)

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
