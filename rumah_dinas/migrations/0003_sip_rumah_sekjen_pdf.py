# Generated manually for SIKARIS SIP Sekjen approval workflow

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rumah_dinas', '0002_siprumahdinas_bukti_bayar_pnbp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siprumahdinas',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('DIAJUKAN', 'Diajukan'), ('DIAJUKAN_SEKJEN', 'Diajukan ke Sekretaris Jenderal'), ('DISETUJUI_SEKJEN', 'Disetujui Sekretaris Jenderal'), ('DITOLAK_SEKJEN', 'Ditolak Sekretaris Jenderal'), ('DISETUJUI', 'Disetujui'), ('MENUNGGU_TTE', 'Menunggu TTE BSrE'), ('AKTIF', 'Aktif'), ('BERAKHIR', 'Berakhir'), ('DICABUT', 'Dicabut'), ('DITOLAK', 'Ditolak'), ('DIBATALKAN', 'Dibatalkan'), ('PENGOSONGAN', 'Dalam Proses Pengosongan')], default='DRAFT', max_length=25),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='jenis_masa_berlaku',
            field=models.CharField(choices=[('TANGGAL', 'Berdasarkan Tanggal'), ('JABATAN', 'Selama Masih Menduduki Jabatan')], default='JABATAN', max_length=20),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='masa_berlaku_sip',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='file_konsep_pdf',
            field=models.FileField(blank=True, null=True, upload_to='sip_rumah_dinas/konsep/'),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='file_final_pdf',
            field=models.FileField(blank=True, null=True, upload_to='sip_rumah_dinas/final/'),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='file_signed_pdf',
            field=models.FileField(blank=True, null=True, upload_to='sip_rumah_dinas/signed/'),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='tanggal_pengajuan',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='tanggal_persetujuan',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='disetujui_oleh',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sip_rumah_disetujui', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='catatan_penolakan',
            field=models.TextField(blank=True, null=True),
        ),
    ]
