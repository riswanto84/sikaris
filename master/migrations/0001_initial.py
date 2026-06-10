# Generated manually for SIKARIS fixed build
import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name='UnitKerja', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('nama_unit', models.CharField(max_length=150, unique=True)), ('keterangan', models.TextField(blank=True, null=True)),
        ], options={'ordering':['nama_unit']}),
        migrations.CreateModel(name='Pegawai', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('nip', models.CharField(max_length=30, unique=True)), ('nik', models.CharField(blank=True, max_length=30, null=True)),
            ('nama', models.CharField(max_length=150)), ('jabatan', models.CharField(blank=True, max_length=150, null=True)),
            ('pangkat', models.CharField(blank=True, max_length=100, null=True)), ('golongan', models.CharField(blank=True, max_length=20, null=True)),
            ('no_hp', models.CharField(blank=True, max_length=30, null=True)), ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ('alamat', models.TextField(blank=True, null=True)), ('status_pegawai', models.CharField(default='Aktif', max_length=50)),
            ('foto', models.ImageField(blank=True, null=True, upload_to='pegawai/')),
            ('unit_kerja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pegawai', to='master.unitkerja')),
        ], options={'ordering':['nama']}),
        migrations.CreateModel(name='Kendaraan', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('kode_kendaraan', models.CharField(max_length=50, unique=True)), ('nomor_polisi', models.CharField(max_length=30, unique=True)),
            ('merek', models.CharField(max_length=100)), ('tipe', models.CharField(blank=True, max_length=100, null=True)),
            ('jenis_kendaraan', models.CharField(blank=True, max_length=50, null=True)), ('tahun_pembuatan', models.PositiveIntegerField(blank=True, null=True)),
            ('tahun_perolehan', models.PositiveIntegerField(blank=True, null=True)), ('warna', models.CharField(blank=True, max_length=50, null=True)),
            ('nomor_rangka', models.CharField(blank=True, max_length=100, null=True)), ('nomor_mesin', models.CharField(blank=True, max_length=100, null=True)),
            ('nomor_bpkb', models.CharField(blank=True, max_length=100, null=True)), ('nomor_stnk', models.CharField(blank=True, max_length=100, null=True)),
            ('masa_berlaku_stnk', models.DateField(blank=True, null=True)), ('jatuh_tempo_pajak', models.DateField(blank=True, null=True)),
            ('nup', models.CharField(blank=True, max_length=100, null=True)), ('kode_barang', models.CharField(blank=True, max_length=100, null=True)),
            ('nilai_perolehan', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
            ('kondisi', models.CharField(choices=[('BAIK','Baik'),('RUSAK_RINGAN','Rusak Ringan'),('RUSAK_BERAT','Rusak Berat')], default='BAIK', max_length=20)),
            ('status_pemanfaatan', models.CharField(choices=[('TERSEDIA','Tersedia'),('DIGUNAKAN','Digunakan'),('DALAM_SERVICE','Dalam Service'),('TIDAK_AKTIF','Tidak Aktif')], default='TERSEDIA', max_length=30)),
            ('kilometer_terakhir', models.PositiveIntegerField(default=0)), ('foto', models.ImageField(blank=True, null=True, upload_to='kendaraan/')),
            ('pengguna', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kendaraan_digunakan', to='master.pegawai')),
            ('unit_kerja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kendaraan', to='master.unitkerja')),
        ], options={'ordering':['nomor_polisi']}),
        migrations.CreateModel(name='RumahDinas', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('kode_rumah', models.CharField(max_length=50, unique=True)), ('nama_rumah', models.CharField(max_length=150)),
            ('jenis_rumah', models.CharField(blank=True, max_length=100, null=True)), ('alamat', models.TextField()),
            ('provinsi', models.CharField(blank=True, max_length=100, null=True)), ('kabupaten_kota', models.CharField(blank=True, max_length=100, null=True)),
            ('kecamatan', models.CharField(blank=True, max_length=100, null=True)), ('kelurahan', models.CharField(blank=True, max_length=100, null=True)),
            ('latitude', models.DecimalField(blank=True, decimal_places=8, max_digits=12, null=True)), ('longitude', models.DecimalField(blank=True, decimal_places=8, max_digits=12, null=True)),
            ('luas_tanah', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)), ('luas_bangunan', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
            ('jumlah_kamar_tidur', models.PositiveIntegerField(default=0)), ('jumlah_kamar_mandi', models.PositiveIntegerField(default=0)),
            ('daya_listrik', models.CharField(blank=True, max_length=50, null=True)), ('tahun_dibangun', models.PositiveIntegerField(blank=True, null=True)),
            ('tahun_perolehan', models.PositiveIntegerField(blank=True, null=True)), ('nup', models.CharField(blank=True, max_length=100, null=True)),
            ('kode_barang', models.CharField(blank=True, max_length=100, null=True)), ('nilai_perolehan', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
            ('nomor_sertifikat', models.CharField(blank=True, max_length=100, null=True)), ('status_tanah', models.CharField(blank=True, max_length=100, null=True)),
            ('kondisi', models.CharField(choices=[('BAIK','Baik'),('RUSAK_RINGAN','Rusak Ringan'),('RUSAK_BERAT','Rusak Berat')], default='BAIK', max_length=20)),
            ('status_pemanfaatan', models.CharField(choices=[('KOSONG','Kosong'),('DIHUNI','Dihuni'),('DALAM_PERBAIKAN','Dalam Perbaikan'),('TIDAK_AKTIF','Tidak Aktif')], default='KOSONG', max_length=30)),
            ('foto_depan', models.ImageField(blank=True, null=True, upload_to='rumah_dinas/')),
        ], options={'ordering':['kode_rumah']}),
    ]
