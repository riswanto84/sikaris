# Generated manually for SIKARIS fixed build
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('master','0001_initial')]
    operations=[
        migrations.CreateModel(name='SIPRumahDinas', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('nomor_sip', models.CharField(max_length=100, unique=True)), ('tanggal_sip', models.DateField()),
            ('tanggal_mulai', models.DateField()), ('tanggal_akhir', models.DateField()),
            ('dasar_penerbitan', models.TextField(blank=True, null=True)), ('pejabat_penandatangan', models.CharField(blank=True, max_length=150, null=True)),
            ('jumlah_anggota_keluarga', models.PositiveIntegerField(default=0)),
            ('status', models.CharField(choices=[('DRAFT','Draft'),('DIAJUKAN','Diajukan'),('DISETUJUI','Disetujui'),('AKTIF','Aktif'),('BERAKHIR','Berakhir'),('DICABUT','Dicabut'),('DITOLAK','Ditolak'),('DIBATALKAN','Dibatalkan'),('PENGOSONGAN','Dalam Proses Pengosongan')], default='DRAFT', max_length=20)),
            ('dokumen_sip', models.FileField(blank=True, null=True, upload_to='sip_rumah_dinas/')), ('dokumen_bast', models.FileField(blank=True, null=True, upload_to='bast_rumah_dinas/')), ('catatan', models.TextField(blank=True, null=True)),
            ('dibuat_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ('pegawai', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sip_rumah', to='master.pegawai')),
            ('rumah_dinas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sip_rumah', to='master.rumahdinas')),
        ], options={'ordering':['-tanggal_sip']}),
        migrations.CreateModel(name='PerbaikanRumahDinas', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('tanggal_laporan', models.DateField()), ('jenis_kerusakan', models.CharField(max_length=100)), ('uraian_kerusakan', models.TextField()),
            ('estimasi_biaya', models.DecimalField(decimal_places=2, default=0, max_digits=18)), ('realisasi_biaya', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
            ('status', models.CharField(default='Dilaporkan', max_length=50)), ('foto_sebelum', models.ImageField(blank=True, null=True, upload_to='perbaikan_rumah/sebelum/')), ('foto_sesudah', models.ImageField(blank=True, null=True, upload_to='perbaikan_rumah/sesudah/')),
            ('pelapor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='master.pegawai')),
            ('rumah_dinas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='perbaikan', to='master.rumahdinas')),
        ]),
    ]
