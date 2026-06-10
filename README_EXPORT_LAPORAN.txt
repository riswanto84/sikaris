Perbaikan fitur Laporan & Export SIKARIS
=========================================

Fitur yang ditambahkan:
1. Tombol export Excel dan PDF di halaman /laporan/.
2. Export laporan kendaraan:
   - Data kendaraan
   - Kondisi kendaraan: Baik/Rusak Ringan/Rusak Berat
   - Status pemanfaatan
   - SIP kendaraan dan pemakai SIP
   - Detail SIP kendaraan
   - Riwayat service kendaraan
   - Riwayat kondisi kendaraan
3. Export laporan rumah dinas:
   - Data rumah dinas
   - Kondisi rumah dinas
   - Status pemanfaatan
   - SIP rumah dinas
   - Pemakai/penghuni rumah dinas
   - Detail pemakai: NIP, jabatan, unit kerja
4. PDF dibuat tanpa library tambahan agar tetap jalan tanpa install reportlab.
5. Excel menggunakan openpyxl yang sudah ada di requirements.txt.

File yang diubah:
- laporan/views.py
- laporan/urls.py
- templates/laporan/index.html

URL export:
- /laporan/kendaraan/excel/
- /laporan/kendaraan/pdf/
- /laporan/rumah-dinas/excel/
- /laporan/rumah-dinas/pdf/

Cara menjalankan:
1. Ekstrak zip.
2. Masuk folder sikaris.
3. Jalankan environment Python Anda.
4. Jalankan: pip install -r requirements.txt
5. Jalankan: python manage.py runserver
6. Buka: http://localhost:8000/laporan/

UPDATE 10-06-2026:
- Export Excel Kendaraan menambahkan kolom Riwayat Pengguna Sebelumnya.
- Export Excel Kendaraan menambahkan sheet Riwayat Pengguna Kendaraan.
- Export Excel Rumah Dinas menambahkan kolom Riwayat Pengguna Sebelumnya.
- Export Excel Rumah Dinas menambahkan sheet Riwayat Pengguna Rumah.
- Export PDF Kendaraan dan Rumah Dinas menampilkan riwayat pengguna sebelumnya.
- Export PDF menampilkan header Kementerian Sosial RI dengan logo Kemensos.
- Tambahan dependency untuk PDF berlogo: reportlab dan svglib.
