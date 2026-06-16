from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('psp', '0002_revisi_psp_bmn'),
        ('core', '0001_nomorsuratsequence'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField('permohonanpspbmn', 'judul_paket', models.CharField(blank=True, help_text='Contoh: PSP BMN Berupa 3.000 Unit Peralatan dan Mesin pada Sekretariat Jenderal', max_length=250, null=True)),
        migrations.AddField('permohonanpspbmn', 'nomor_tiket_siman', models.CharField(blank=True, help_text='Nomor tiket terdaftar pada SIMAN V2, contoh: PP126010610424145813', max_length=80, null=True)),
        migrations.AddField('permohonanpspbmn', 'kode_satuan_kerja', models.CharField(blank=True, max_length=120, null=True)),
        migrations.AddField('permohonanpspbmn', 'nama_satuan_kerja', models.CharField(blank=True, max_length=220, null=True)),
        migrations.AddField('permohonanpspbmn', 'batas_nilai_per_unit', models.DecimalField(decimal_places=2, default=100000000, max_digits=20)),
        migrations.AddField('permohonanpspbmn', 'jumlah_barang', models.PositiveIntegerField(default=0)),
        migrations.AddField('permohonanpspbmn', 'total_nilai_barang', models.DecimalField(decimal_places=2, default=0, max_digits=24)),
        migrations.AddField('permohonanpspbmn', 'nilai_tertinggi_per_unit', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
        migrations.AddField('permohonanpspbmn', 'ada_barang_diatas_100jt', models.BooleanField(default=False)),
        migrations.AddField('permohonanpspbmn', 'nomor_nota_permohonan_psp', models.CharField(blank=True, help_text='Format otomatis: nomor/1.5/PL.04/bulan/tahun', max_length=120, null=True)),
        migrations.AddField('permohonanpspbmn', 'tanggal_nota_permohonan_psp', models.DateField(blank=True, null=True)),
        migrations.AddField('permohonanpspbmn', 'nomor_surat_keterangan_digital', models.CharField(blank=True, max_length=120, null=True)),
        migrations.AddField('permohonanpspbmn', 'tanggal_surat_keterangan_digital', models.DateField(blank=True, null=True)),
        migrations.AddField('permohonanpspbmn', 'nomor_surat_pernyataan_formil_materiil', models.CharField(blank=True, max_length=120, null=True)),
        migrations.AddField('permohonanpspbmn', 'tanggal_surat_pernyataan_formil_materiil', models.DateField(blank=True, null=True)),
        migrations.AddField('permohonanpspbmn', 'nomor_nota_biro_hukum', models.CharField(blank=True, max_length=120, null=True)),
        migrations.AddField('permohonanpspbmn', 'tanggal_nota_biro_hukum', models.DateField(blank=True, null=True)),
        migrations.AddField('permohonanpspbmn', 'catatan_biro_hukum', models.TextField(blank=True, null=True)),
        migrations.AddField('permohonanpspbmn', 'disetujui_sekjen_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='psp_disetujui_sekjen', to=settings.AUTH_USER_MODEL)),
        migrations.AddField('permohonanpspbmn', 'tanggal_persetujuan_sekjen', models.DateField(blank=True, null=True)),
        migrations.AddField('permohonanpspbmn', 'status_tte', models.CharField(choices=[('BELUM', 'Belum TTE BSrE'), ('SIAP_TTE', 'Siap TTE BSrE'), ('PROSES_TTE', 'Proses TTE BSrE'), ('SUDAH_TTE', 'Sudah TTE BSrE'), ('DITOLAK_TTE', 'Ditolak TTE BSrE')], default='BELUM', max_length=20)),
        migrations.AddField('permohonanpspbmn', 'pejabat_tte', models.CharField(blank=True, help_text='Nama/jabatan pejabat TTE BSrE', max_length=180, null=True)),
        migrations.AddField('permohonanpspbmn', 'nip_pejabat_tte', models.CharField(blank=True, max_length=30, null=True)),
        migrations.AddField('permohonanpspbmn', 'tanggal_tte', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('permohonanpspbmn', 'file_sebelum_tte', models.FileField(blank=True, null=True, upload_to='psp/tte/sebelum/')),
        migrations.AddField('permohonanpspbmn', 'file_setelah_tte', models.FileField(blank=True, null=True, upload_to='psp/tte/setelah/')),
        migrations.AddField('permohonanpspbmn', 'status_emeterai', models.CharField(choices=[('TIDAK_WAJIB', 'Tidak Wajib'), ('BELUM', 'Belum e-Meterai'), ('SUDAH', 'Sudah e-Meterai'), ('GAGAL', 'Gagal/Perlu Perbaikan')], default='TIDAK_WAJIB', max_length=20)),
        migrations.AddField('permohonanpspbmn', 'nomor_serial_emeterai', models.CharField(blank=True, max_length=120, null=True)),
        migrations.AddField('permohonanpspbmn', 'tanggal_emeterai', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('permohonanpspbmn', 'dokumen_bermeterai', models.FileField(blank=True, null=True, upload_to='psp/emeterai/')),
        migrations.AlterField('permohonanpspbmn', 'jenis_barang', models.CharField(choices=[('KENDARAAN', 'Kendaraan'), ('RUMAH_NEGARA', 'Rumah Negara'), ('TANAH_NEGARA', 'Tanah Negara'), ('PERALATAN_MESIN', 'Peralatan dan Mesin'), ('LAINNYA', 'BMN Lainnya')], max_length=30)),
        migrations.AlterField('permohonanpspbmn', 'nomor_sk_psp', models.CharField(blank=True, help_text='Format otomatis SK: nomor/HUK/tahun', max_length=150, null=True)),
        migrations.AlterField('permohonanpspbmn', 'status', models.CharField(choices=[('DRAFT', 'Draft'), ('VALIDASI_DATA', 'Validasi Data'), ('DIAJUKAN', 'Diajukan Unit Kerja'), ('DIVERIFIKASI_BIRO', 'Diverifikasi Biro Umum'), ('PERLU_PERBAIKAN', 'Perlu Perbaikan Usulan'), ('SIAP_DIAJUKAN_SEKJEN', 'Siap Diajukan ke Sekjen'), ('DIAJUKAN_SEKJEN', 'Diajukan ke Sekjen'), ('DISETUJUI_SEKJEN', 'Disetujui Sekjen'), ('DIAJUKAN_BIRO_HUKUM', 'Diajukan ke Biro Hukum'), ('REVISI_DRAFT_SK', 'Revisi Draf SK'), ('SK_TERBIT', 'SK PSP Terbit'), ('DITOLAK', 'Ditolak'), ('DISETUJUI', 'Disetujui'), ('PROSES_PSP', 'Proses Penetapan PSP'), ('SELESAI', 'Selesai')], default='DIAJUKAN', max_length=40)),
        migrations.CreateModel(
            name='BarangPSP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nomor_urut', models.PositiveIntegerField(default=1)),
                ('kode_satuan_kerja', models.CharField(blank=True, max_length=120, null=True)),
                ('nama_satuan_kerja', models.CharField(blank=True, max_length=220, null=True)),
                ('kode_barang', models.CharField(max_length=100)),
                ('nup', models.CharField(max_length=100)),
                ('nama_barang', models.CharField(max_length=220)),
                ('tipe_barang', models.CharField(blank=True, max_length=250, null=True)),
                ('tahun_perolehan', models.CharField(blank=True, max_length=30, null=True)),
                ('kuantitas', models.PositiveIntegerField(default=1)),
                ('nilai_perolehan', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('nilai_total', models.DecimalField(decimal_places=2, default=0, max_digits=22)),
                ('kondisi_barang', models.CharField(choices=[('BAIK', 'Baik'), ('RUSAK_RINGAN', 'Rusak Ringan'), ('RUSAK_BERAT', 'Rusak Berat'), ('LAINNYA', 'Lainnya')], default='BAIK', max_length=30)),
                ('keterangan', models.TextField(blank=True, null=True)),
                ('permohonan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detail_barang', to='psp.permohonanpspbmn')),
            ],
            options={
                'verbose_name': 'Detail Barang PSP',
                'verbose_name_plural': 'Detail Barang PSP',
                'ordering': ['nomor_urut', 'id'],
                'unique_together': {('permohonan', 'kode_barang', 'nup')},
            },
        ),
    ]
