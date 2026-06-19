PERBAIKAN TAMPILAN SIM PENGELOLAAN BMN - 19 Juni 2026

Isi paket source code ini:
1. Nama aplikasi pada template utama dan login diubah menjadi SIM PENGELOLAAN BMN.
2. Logo Kementerian Sosial tetap dipertahankan pada login dan sidebar.
3. Template login diperbarui dengan layout modern dua panel.
4. Template base/sidebar diperbarui dengan menu modern, warna biru Kemensos, ikon seragam, dan section menu yang lebih rapi.
5. Ditambahkan tema CSS baru: static/css/sim_bmn_theme.css.
6. Struktur menu mencakup modul:
   - Master Data
   - SIP Kendaraan
   - SIP Rumah Negara
   - SIP Barang Lainnya
   - Persetujuan SIP
   - Pemeliharaan Kendaraan
   - Penghapusan BMN
   - PSP BMN
   - Laporan & Export
   - Tanah Negara
   - Pengaturan
7. Fitur SIP Barang Lainnya tetap memakai nomor SIP manual dan daftar barang multi-item.
8. Preview tampilan disertakan pada file: _preview_tampilan_menu_sim_pengelolaan_bmn.png

Cara pakai:
1. Ekstrak ZIP ini.
2. Copy/replace ke folder project Django SIM Pengelolaan BMN.
3. Jalankan server:
   python manage.py runserver

Catatan:
- Perubahan ini fokus pada source code tampilan/template dan fitur SIP Barang Lainnya yang sudah dibuat sebelumnya.
- Tidak ada perubahan database khusus untuk tampilan UI, tetapi fitur SIP Barang Lainnya tetap membutuhkan migration yang sudah disertakan di folder barang_lainnya/migrations.
