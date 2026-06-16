from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0009_unitkerja_penerbit_sip_kendaraan'),
        ('kendaraan', '0006_nomor_sip_otomatis_tte'),
    ]

    operations = [
        migrations.AddField(
            model_name='sipkendaraan',
            name='pejabat_penerbit_sip_kendaraan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sip_kendaraan_diterbitkan', to='master.pegawai'),
        ),
        migrations.AddField(
            model_name='sipkendaraan',
            name='nama_pejabat_penerbit_sip_kendaraan',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='sipkendaraan',
            name='nip_pejabat_penerbit_sip_kendaraan',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='sipkendaraan',
            name='jabatan_pejabat_penerbit_sip_kendaraan',
            field=models.CharField(blank=True, max_length=180, null=True),
        ),
        migrations.AddField(
            model_name='sipkendaraan',
            name='status_tte',
            field=models.CharField(choices=[('BELUM', 'Belum TTE'), ('SIAP_TTE', 'Siap TTE'), ('PROSES_TTE', 'Proses TTE'), ('SUDAH_TTE', 'Sudah TTE'), ('DITOLAK_TTE', 'Ditolak TTE')], default='BELUM', max_length=20),
        ),
        migrations.AddField(
            model_name='sipkendaraan',
            name='tanggal_tte',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sipkendaraan',
            name='catatan_tte',
            field=models.TextField(blank=True, null=True),
        ),
    ]
