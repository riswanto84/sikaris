# Generated manually for SIKARIS
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0007_status_pemanfaatan_keterangan'),
    ]

    operations = [
        migrations.AddField(
            model_name='rumahdinas',
            name='dokumen_sertifikat',
            field=models.FileField(blank=True, null=True, upload_to='rumah_dinas/dokumen/sertifikat/'),
        ),
    ]
