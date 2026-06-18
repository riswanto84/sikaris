# Generated manually to fix choices max_length validation
from django.db import migrations, models
import core.constants


class Migration(migrations.Migration):

    dependencies = [
        ('kendaraan', '0012_alter_sipkendaraan_nomor_sip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sipkendaraan',
            name='jenis_pemakaian',
            field=models.CharField(blank=True, choices=core.constants.JENIS_KENDARAAN_CHOICES, max_length=100, null=True, verbose_name='Jenis Kendaraan'),
        ),
    ]
