from django.db import models, transaction
from django.utils import timezone


class NomorSuratSequence(models.Model):
    """Counter penomoran surat otomatis per jenis dokumen dan tahun.

    Format default mengikuti format SIKARIS:
    1/1.5/PL.03/SIKARIS/01/2026
    Untuk SK HUK:
    72/HUK/2026
    """

    jenis = models.CharField(max_length=60)
    tahun = models.PositiveIntegerField()
    nomor_terakhir = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('jenis', 'tahun')
        ordering = ['jenis', 'tahun']
        verbose_name = 'Sequence Nomor Surat'
        verbose_name_plural = 'Sequence Nomor Surat'

    def __str__(self):
        return f'{self.jenis}/{self.tahun}: {self.nomor_terakhir}'


def next_nomor_surat(
    jenis,
    tanggal=None,
    *,
    kode_unit='1.5',
    kode_klasifikasi='PL.04',
    kode_aplikasi='SIKARIS',
    format_surat='BIRO_UMUM',
    start=1,
):
    """Ambil nomor surat berikutnya secara aman.

    format_surat:
    - BIRO_UMUM -> nomor/kode_unit/kode_klasifikasi/SIKARIS/bulan/tahun, contoh 1/1.5/PL.03/SIKARIS/01/2026
    - HUK       -> 72/HUK/2026
    - SIMPLE    -> PSP-BMN/2026/00001
    """
    tanggal = tanggal or timezone.now().date()
    tahun = tanggal.year
    bulan = tanggal.month
    with transaction.atomic():
        seq, created = NomorSuratSequence.objects.select_for_update().get_or_create(
            jenis=jenis,
            tahun=tahun,
            defaults={'nomor_terakhir': max(start - 1, 0)},
        )
        # Sinkronkan sequence dengan nomor terakhir dari data transaksi
        # ketika parameter start dikirim dari model. Ini menjaga penomoran
        # otomatis tetap meneruskan nomor sebelumnya walaupun sequence
        # belum pernah dibuat atau tertinggal dari data lama.
        min_last = max(start - 1, 0)
        if seq.nomor_terakhir < min_last:
            seq.nomor_terakhir = min_last
        seq.nomor_terakhir += 1
        seq.save(update_fields=['nomor_terakhir', 'updated_at'])
        nomor = seq.nomor_terakhir

    if format_surat == 'HUK':
        return f'{nomor}/HUK/{tahun}'
    if format_surat == 'SIMPLE':
        return f'{jenis}/{tahun}/{nomor:05d}'
    return f'{nomor}/{kode_unit}/{kode_klasifikasi}/{kode_aplikasi}/{bulan:02d}/{tahun}'
