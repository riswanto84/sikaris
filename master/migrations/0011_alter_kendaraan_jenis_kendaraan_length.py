# Generated manually to fix choices max_length validation
from django.db import migrations, models
import core.constants


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0010_master_siman_fields_and_locks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kendaraan',
            name='jenis_kendaraan',
            field=models.CharField(blank=True, choices=core.constants.JENIS_KENDARAAN_CHOICES, max_length=100, null=True),
        ),
    ]
