# Generated for jenis kendaraan choices and SIP label update
from django.db import migrations, models
import core.constants


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0003_fotorumahdinas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kendaraan',
            name='jenis_kendaraan',
            field=models.CharField(blank=True, choices=core.constants.JENIS_KENDARAAN_CHOICES, max_length=30, null=True),
        ),
    ]
