from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0008_rumahdinas_dokumen_sertifikat'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitkerja',
            name='jenis_unit',
            field=models.CharField(choices=[('BIRO_UMUM', 'Biro Umum'), ('DITJEN', 'Direktorat Jenderal / Sekretariat Ditjen'), ('ITJEN', 'Inspektorat Jenderal / Sekretariat Itjen'), ('BADAN', 'Badan'), ('PUSAT', 'Pusat'), ('SENTRA', 'Sentra'), ('BALAI', 'Balai'), ('LAINNYA', 'Lainnya')], default='LAINNYA', help_text='Dipakai untuk menentukan pejabat penerbit SIP Kendaraan.', max_length=30),
        ),
        migrations.AddField(
            model_name='unitkerja',
            name='nama_jabatan_penerbit_sip_kendaraan',
            field=models.CharField(blank=True, help_text='Contoh: Kepala Biro Umum, Sekretaris Ditjen Rehabilitasi Sosial, Kepala Sentra, Kepala Balai.', max_length=180, null=True),
        ),
        migrations.AddField(
            model_name='unitkerja',
            name='pejabat_penerbit_sip_kendaraan',
            field=models.ForeignKey(blank=True, help_text='Pegawai yang menjadi pejabat penerbit/penandatangan SIP Kendaraan untuk unit ini.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unit_penerbit_sip_kendaraan', to='master.pegawai'),
        ),
    ]
