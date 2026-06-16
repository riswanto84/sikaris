from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rumah_dinas', '0003_sip_rumah_sekjen_pdf'),
        ('core', '0001_nomorsuratsequence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siprumahdinas',
            name='nomor_sip',
            field=models.CharField(blank=True, help_text='Otomatis dari sistem jika dikosongkan. Format: nomor/1.5/PL.04/bulan/tahun', max_length=100, unique=True),
        ),
    ]
