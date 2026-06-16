from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penghapusan', '0002_foto_kondisi_multi'),
    ]

    operations = [
        migrations.AddField(
            model_name='permohonanpenghapusanbmn',
            name='status_tte',
            field=models.CharField(choices=[('BELUM', 'Belum TTE'), ('SIAP_TTE', 'Siap TTE'), ('PROSES_TTE', 'Proses TTE'), ('SUDAH_TTE', 'Sudah TTE'), ('DITOLAK_TTE', 'Ditolak TTE')], default='BELUM', max_length=20),
        ),
        migrations.AddField(
            model_name='permohonanpenghapusanbmn',
            name='pejabat_tte',
            field=models.CharField(blank=True, max_length=180, null=True),
        ),
        migrations.AddField(
            model_name='permohonanpenghapusanbmn',
            name='nip_pejabat_tte',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='permohonanpenghapusanbmn',
            name='tanggal_tte',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='permohonanpenghapusanbmn',
            name='file_sebelum_tte',
            field=models.FileField(blank=True, null=True, upload_to='penghapusan/tte/sebelum/'),
        ),
        migrations.AddField(
            model_name='permohonanpenghapusanbmn',
            name='file_setelah_tte',
            field=models.FileField(blank=True, null=True, upload_to='penghapusan/tte/setelah/'),
        ),
        migrations.AddField(
            model_name='permohonanpenghapusanbmn',
            name='catatan_tte',
            field=models.TextField(blank=True, null=True),
        ),
    ]
