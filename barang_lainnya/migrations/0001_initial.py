from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master', '0013_kendaraan_pejabat_penandatangan_sip'),
    ]

    operations = [
        migrations.CreateModel(
            name='SIPBarangLainnya',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nomor_sip', models.CharField(help_text='Nomor SIP diinput manual oleh pengguna.', max_length=100, unique=True)),
                ('tanggal_sip', models.DateField(default=django.utils.timezone.now)),
                ('tanggal_mulai', models.DateField()),
                ('tanggal_akhir', models.DateField()),
                ('dasar_penerbitan', models.TextField(blank=True, null=True)),
                ('tujuan_penggunaan', models.TextField(blank=True, null=True)),
                ('lokasi_penggunaan', models.CharField(blank=True, max_length=255, null=True)),
                ('nama_pejabat_penandatangan', models.CharField(blank=True, max_length=150, null=True)),
                ('nip_pejabat_penandatangan', models.CharField(blank=True, max_length=30, null=True)),
                ('jabatan_pejabat_penandatangan', models.CharField(blank=True, max_length=180, null=True)),
                ('keterangan_tambahan', models.TextField(blank=True, null=True)),
                ('dokumen_pendukung', models.FileField(blank=True, null=True, upload_to='sip_barang_lainnya/lampiran/')),
                ('file_konsep_pdf', models.FileField(blank=True, null=True, upload_to='sip_barang_lainnya/konsep/')),
                ('file_signed_pdf', models.FileField(blank=True, null=True, upload_to='sip_barang_lainnya/signed/')),
                ('status_tte', models.CharField(choices=[('BELUM', 'Belum TTE'), ('SUDAH_TTE', 'Sudah TTE')], default='BELUM', max_length=20)),
                ('tanggal_tte', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft/Konsep'), ('DIAJUKAN', 'Diajukan'), ('DITOLAK', 'Ditolak'), ('TERBIT', 'Terbit')], default='DRAFT', max_length=20)),
                ('tanggal_pengajuan', models.DateTimeField(blank=True, null=True)),
                ('tanggal_persetujuan', models.DateTimeField(blank=True, null=True)),
                ('catatan', models.TextField(blank=True, null=True)),
                ('catatan_penolakan', models.TextField(blank=True, null=True)),
                ('dibuat_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sip_barang_lainnya_dibuat', to=settings.AUTH_USER_MODEL)),
                ('disetujui_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sip_barang_lainnya_disetujui', to=settings.AUTH_USER_MODEL)),
                ('pejabat_penandatangan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sip_barang_lainnya_penandatangan', to='master.pegawai')),
                ('pemegang_sip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sip_barang_lainnya_pemegang', to='master.pegawai')),
                ('pengguna_aktual', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sip_barang_lainnya_pengguna', to='master.pegawai')),
            ],
            options={'ordering': ['-tanggal_sip', '-created_at']},
        ),
        migrations.CreateModel(
            name='SIPBarangLainnyaItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('urutan', models.PositiveIntegerField(default=1)),
                ('nama_barang', models.CharField(max_length=200)),
                ('spesifikasi', models.CharField(blank=True, max_length=255, null=True)),
                ('satuan', models.CharField(default='Unit', max_length=50)),
                ('jumlah', models.PositiveIntegerField(default=1)),
                ('nup', models.CharField(blank=True, max_length=100, null=True)),
                ('serial_number', models.CharField(blank=True, max_length=150, null=True)),
                ('keterangan', models.CharField(blank=True, max_length=255, null=True)),
                ('sip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='barang_lainnya.sipbaranglainnya')),
            ],
            options={'ordering': ['urutan', 'id']},
        ),
    ]
