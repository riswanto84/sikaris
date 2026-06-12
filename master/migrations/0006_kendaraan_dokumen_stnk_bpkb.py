# Generated manually for SIKARIS

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0005_rumahdinas_unit_kerja'),
    ]

    operations = [
        migrations.AddField(
            model_name='kendaraan',
            name='dokumen_stnk',
            field=models.FileField(blank=True, null=True, upload_to='kendaraan/dokumen/stnk/'),
        ),
        migrations.AddField(
            model_name='kendaraan',
            name='dokumen_bpkb',
            field=models.FileField(blank=True, null=True, upload_to='kendaraan/dokumen/bpkb/'),
        ),
    ]
