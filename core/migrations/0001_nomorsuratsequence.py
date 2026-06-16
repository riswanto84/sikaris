from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NomorSuratSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jenis', models.CharField(max_length=60)),
                ('tahun', models.PositiveIntegerField()),
                ('nomor_terakhir', models.PositiveIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Sequence Nomor Surat',
                'verbose_name_plural': 'Sequence Nomor Surat',
                'ordering': ['jenis', 'tahun'],
                'unique_together': {('jenis', 'tahun')},
            },
        ),
    ]
