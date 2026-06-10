# Generated for SIP jenis kendaraan choices
from django.db import migrations, models
import core.constants


class Migration(migrations.Migration):

    dependencies = [
        ('kendaraan', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sipkendaraan',
            name='jenis_pemakaian',
            field=models.CharField('Jenis Kendaraan', blank=True, choices=core.constants.JENIS_KENDARAAN_CHOICES, max_length=30, null=True),
        ),
    ]
