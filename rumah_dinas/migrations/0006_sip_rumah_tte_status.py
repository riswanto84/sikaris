from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rumah_dinas', '0005_alter_siprumahdinas_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='siprumahdinas',
            name='status_tte',
            field=models.CharField(choices=[('BELUM', 'Belum TTE'), ('SIAP_TTE', 'Siap TTE'), ('PROSES_TTE', 'Proses TTE'), ('SUDAH_TTE', 'Sudah TTE'), ('DITOLAK_TTE', 'Ditolak TTE')], default='BELUM', max_length=20),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='tanggal_tte',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='siprumahdinas',
            name='catatan_tte',
            field=models.TextField(blank=True, null=True),
        ),
    ]
