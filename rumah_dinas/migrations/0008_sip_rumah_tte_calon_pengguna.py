# Generated manually for SIKARIS

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rumah_dinas', '0007_alter_siprumahdinas_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='siprumahdinas',
            name='file_tte_calon_pengguna',
            field=models.FileField(blank=True, null=True, upload_to='sip_rumah_dinas/tte_calon_pengguna/'),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='status_tte_calon_pengguna',
            field=models.CharField(choices=[('BELUM', 'Belum TTE Calon Pengguna'), ('SUDAH_TTE', 'Sudah TTE Calon Pengguna')], default='BELUM', max_length=20),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='tanggal_tte_calon_pengguna',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='catatan_tte_calon_pengguna',
            field=models.TextField(blank=True, null=True),
        ),
    ]
