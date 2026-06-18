from django.db import migrations, models
import re


def clean_nup_numeric(apps, schema_editor):
    for model_name in ['Kendaraan', 'RumahDinas']:
        Model = apps.get_model('master', model_name)
        for obj in Model.objects.all().only('id', 'nup'):
            value = getattr(obj, 'nup', None)
            if value in [None, '']:
                continue
            value_str = str(value).strip()
            if not re.fullmatch(r'\d+', value_str):
                setattr(obj, 'nup', None)
                obj.save(update_fields=['nup'])



class Migration(migrations.Migration):

    dependencies = [
        ('master', '0009_unitkerja_penerbit_sip_kendaraan'),
    ]

    operations = [
        migrations.RunPython(clean_nup_numeric, migrations.RunPython.noop),
        migrations.AddField(
            model_name='unitkerja',
            name='kode_satker',
            field=models.CharField(blank=True, help_text='Kode Satker dari SIMAN, non-editable pada form manual.', max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='kendaraan',
            name='tanggal_perolehan',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='kendaraan',
            name='kode_satker',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='kendaraan',
            name='nup',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rumahdinas',
            name='njop_per_meter_tanah',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Editable oleh operator sesuai data NJOP terbaru.', max_digits=18, verbose_name='Nilai NJOP/m Tanah'),
        ),
        migrations.AddField(
            model_name='rumahdinas',
            name='jumlah_lantai',
            field=models.PositiveIntegerField(default=1, help_text='Tarikan SIMAN.'),
        ),
        migrations.AddField(
            model_name='rumahdinas',
            name='tanggal_perolehan',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='rumahdinas',
            name='nup',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rumahdinas',
            name='kode_satker',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='rumahdinas',
            name='status_penggunaan',
            field=models.CharField(blank=True, help_text='Tarikan SIMAN, non-editable pada form manual.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='rumahdinas',
            name='status_hukum',
            field=models.CharField(choices=[('TIDAK_ADA_SENGKETA', 'Tidak ada sengketa'), ('SENGKETA', 'Sengketa')], default='TIDAK_ADA_SENGKETA', max_length=30),
        ),
    ]
