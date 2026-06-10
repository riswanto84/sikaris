# Generated manually for SIKARIS fixed build
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('master','0001_initial')]
    operations=[
        migrations.CreateModel(name='SIPKendaraan', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('nomor_sip', models.CharField(max_length=100, unique=True)), ('tanggal_sip', models.DateField()),
            ('tanggal_mulai', models.DateField()), ('tanggal_akhir', models.DateField()),
            ('jenis_pemakaian', models.CharField(blank=True, max_length=100, null=True)), ('tujuan_pemakaian', models.TextField(blank=True, null=True)),
            ('lokasi_penggunaan', models.CharField(blank=True, max_length=200, null=True)), ('dasar_penerbitan', models.TextField(blank=True, null=True)),
            ('pejabat_penandatangan', models.CharField(blank=True, max_length=150, null=True)),
            ('status', models.CharField(choices=[('DRAFT','Draft'),('DIAJUKAN','Diajukan'),('DISETUJUI','Disetujui'),('AKTIF','Aktif'),('BERAKHIR','Berakhir'),('DICABUT','Dicabut'),('DITOLAK','Ditolak'),('DIBATALKAN','Dibatalkan')], default='DRAFT', max_length=20)),
            ('dokumen_sip', models.FileField(blank=True, null=True, upload_to='sip_kendaraan/')), ('catatan', models.TextField(blank=True, null=True)),
            ('dibuat_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ('kendaraan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sip_kendaraan', to='master.kendaraan')),
            ('pegawai', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sip_kendaraan', to='master.pegawai')),
        ], options={'ordering':['-tanggal_sip']}),
        migrations.CreateModel(name='ServiceKendaraan', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('tanggal_service', models.DateField()), ('jenis_service', models.CharField(choices=[('SERVICE_BERKALA','Service Berkala'),('GANTI_OLI','Ganti Oli'),('GANTI_BAN','Ganti Ban'),('GANTI_AKI','Ganti Aki'),('PERBAIKAN_MESIN','Perbaikan Mesin'),('PERBAIKAN_BODY','Perbaikan Body'),('LAINNYA','Lainnya')], max_length=50)),
            ('kilometer', models.PositiveIntegerField(blank=True, null=True)), ('bengkel', models.CharField(blank=True, max_length=150, null=True)),
            ('uraian_pekerjaan', models.TextField()), ('sparepart_diganti', models.TextField(blank=True, null=True)),
            ('biaya_jasa', models.DecimalField(decimal_places=2, default=0, max_digits=18)), ('biaya_sparepart', models.DecimalField(decimal_places=2, default=0, max_digits=18)), ('total_biaya', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
            ('kondisi_sebelum', models.CharField(choices=[('BAIK','Baik'),('RUSAK_RINGAN','Rusak Ringan'),('RUSAK_BERAT','Rusak Berat')], max_length=20)),
            ('kondisi_sesudah', models.CharField(choices=[('BAIK','Baik'),('RUSAK_RINGAN','Rusak Ringan'),('RUSAK_BERAT','Rusak Berat')], max_length=20)),
            ('dokumen_bukti', models.FileField(blank=True, null=True, upload_to='service_kendaraan/dokumen/')), ('foto_sebelum', models.ImageField(blank=True, null=True, upload_to='service_kendaraan/sebelum/')), ('foto_sesudah', models.ImageField(blank=True, null=True, upload_to='service_kendaraan/sesudah/')),
            ('dicatat_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ('kendaraan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service', to='master.kendaraan')),
        ], options={'ordering':['-tanggal_service']}),
        migrations.CreateModel(name='RiwayatKondisiKendaraan', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('tanggal', models.DateField()), ('kondisi', models.CharField(choices=[('BAIK','Baik'),('RUSAK_RINGAN','Rusak Ringan'),('RUSAK_BERAT','Rusak Berat')], max_length=20)),
            ('uraian_kondisi', models.TextField(blank=True, null=True)), ('foto_kondisi', models.ImageField(blank=True, null=True, upload_to='kondisi_kendaraan/')),
            ('dicatat_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ('kendaraan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='riwayat_kondisi', to='master.kendaraan')),
        ], options={'ordering':['-tanggal']}),
    ]
