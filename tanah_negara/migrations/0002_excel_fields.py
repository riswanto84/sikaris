# Generated for SIKARIS Tanah Negara Excel field alignment
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tanah_negara', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='tanahnegara', name='kode_satker', field=models.CharField(blank=True, max_length=120, null=True)),
        migrations.AddField(model_name='tanahnegara', name='nama_satker', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='tanahnegara', name='nama_barang', field=models.CharField(blank=True, max_length=220, null=True)),
        migrations.AddField(model_name='tanahnegara', name='nama_aset', field=models.CharField(blank=True, max_length=220, null=True)),
        migrations.AddField(model_name='tanahnegara', name='status_bmn', field=models.CharField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='tanahnegara', name='kondisi', field=models.CharField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='tanahnegara', name='intra_extra', field=models.CharField(blank=True, max_length=50, null=True)),
        migrations.AddField(model_name='tanahnegara', name='jenis_dokumen', field=models.CharField(blank=True, max_length=255, null=True)),
        migrations.AddField(model_name='tanahnegara', name='nomor_dokumen', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='status_sertifikasi', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='jenis_sertipikat', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='atas_nama_sertifikat', field=models.CharField(blank=True, max_length=220, null=True)),
        migrations.AddField(model_name='tanahnegara', name='tanggal_buku_pertama', field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='tanahnegara', name='tanggal_perolehan', field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='tanahnegara', name='nilai_buku', field=models.DecimalField(decimal_places=2, default=0, max_digits=20)),
        migrations.AddField(model_name='tanahnegara', name='luas_tanah_seluruhnya', field=models.DecimalField(decimal_places=2, default=0, max_digits=16)),
        migrations.AddField(model_name='tanahnegara', name='luas_tanah_untuk_bangunan', field=models.DecimalField(decimal_places=2, default=0, max_digits=16)),
        migrations.AddField(model_name='tanahnegara', name='luas_tanah_untuk_sarana_lingkungan', field=models.DecimalField(decimal_places=2, default=0, max_digits=16)),
        migrations.AddField(model_name='tanahnegara', name='luas_lahan_kosong', field=models.DecimalField(decimal_places=2, default=0, max_digits=16)),
        migrations.AddField(model_name='tanahnegara', name='luas_pemanfaatan', field=models.DecimalField(decimal_places=2, default=0, max_digits=16)),
        migrations.AddField(model_name='tanahnegara', name='jumlah_foto', field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name='tanahnegara', name='status_penggunaan', field=models.CharField(blank=True, max_length=255, null=True)),
        migrations.AddField(model_name='tanahnegara', name='status_pemanfaatan', field=models.CharField(blank=True, max_length=255, null=True)),
        migrations.AddField(model_name='tanahnegara', name='no_psp', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='tanggal_psp', field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='tanahnegara', name='rt_rw', field=models.CharField(blank=True, max_length=80, null=True)),
        migrations.AddField(model_name='tanahnegara', name='kelurahan_desa', field=models.CharField(blank=True, max_length=120, null=True)),
        migrations.AddField(model_name='tanahnegara', name='kode_kab_kota', field=models.CharField(blank=True, max_length=80, null=True)),
        migrations.AddField(model_name='tanahnegara', name='kode_provinsi', field=models.CharField(blank=True, max_length=80, null=True)),
        migrations.AddField(model_name='tanahnegara', name='kode_pos', field=models.CharField(blank=True, max_length=20, null=True)),
        migrations.AddField(model_name='tanahnegara', name='sbsk', field=models.DecimalField(decimal_places=2, default=0, max_digits=16)),
        migrations.AddField(model_name='tanahnegara', name='optimalisasi', field=models.DecimalField(decimal_places=2, default=0, max_digits=16)),
        migrations.AddField(model_name='tanahnegara', name='penghuni', field=models.CharField(blank=True, max_length=220, null=True)),
        migrations.AddField(model_name='tanahnegara', name='pengguna', field=models.CharField(blank=True, max_length=220, null=True)),
        migrations.AddField(model_name='tanahnegara', name='kode_kpknl', field=models.CharField(blank=True, max_length=80, null=True)),
        migrations.AddField(model_name='tanahnegara', name='uraian_kpknl', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='uraian_kanwil_djkn', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='nama_kl', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='nama_e1', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='nama_korwil', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='kode_register', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AddField(model_name='tanahnegara', name='status_pmk', field=models.CharField(blank=True, max_length=180, null=True)),
        migrations.AlterField(model_name='tanahnegara', name='nama_tanah', field=models.CharField(max_length=220)),
        migrations.AlterField(model_name='tanahnegara', name='nilai_perolehan', field=models.DecimalField(decimal_places=2, default=0, max_digits=20)),
        migrations.AlterField(model_name='tanahnegara', name='nomor_sertifikat', field=models.CharField(blank=True, max_length=180, null=True)),
    ]
