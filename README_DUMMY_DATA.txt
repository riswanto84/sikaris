PANDUAN DATA DUMMY SIKARIS
==========================

File ini menjelaskan cara mengisi database dengan data dummy untuk uji coba aplikasi.

Data yang dibuat:
- 100 Pegawai
- 100 Kendaraan
- 100 Rumah Dinas
- 100 SIP Kendaraan
- 100 SIP Rumah Dinas
- 100 Service Kendaraan
- 100 Riwayat Kondisi Kendaraan
- 10 Unit Kerja Dummy sebagai referensi pegawai/kendaraan

File command yang ditambahkan:
core/management/commands/generate_dummy_data.py

CARA INJECT KE DATABASE
=======================

1. Extract ZIP project SIKARIS.
2. Masuk ke folder project yang berisi manage.py:

   cd sikaris

3. Aktifkan virtual environment jika ada:

   Mac/Linux:
   source venv/bin/activate

   Windows:
   venv\Scripts\activate

4. Install dependency:

   pip install -r requirements.txt

5. Pastikan migrasi database sudah jalan:

   python manage.py migrate

6. Generate data dummy:

   python manage.py generate_dummy_data

7. Jalankan aplikasi:

   python manage.py runserver

8. Buka browser:

   http://localhost:8000/

CARA GENERATE ULANG DATA DUMMY
==============================

Jika ingin menghapus data dummy lama lalu membuat ulang 100 data baru:

   python manage.py generate_dummy_data --clear

Jika ingin jumlah selain 100, misalnya 200 data:

   python manage.py generate_dummy_data --jumlah 200 --clear

CATATAN PENTING
===============

- Command ini hanya menghapus data dummy yang memiliki prefix DMY saat memakai opsi --clear.
- Data asli yang tidak memakai prefix DMY tidak ikut dihapus.
- Prefix data dummy:
  - Pegawai: NIP diawali DMY
  - Kendaraan: kode diawali DMY-KDR-
  - Rumah Dinas: kode diawali DMY-RD-
  - SIP Kendaraan: nomor diawali DMY-SIP-KDR-
  - SIP Rumah Dinas: nomor diawali DMY-SIP-RD-
- Data SIP dibuat dengan variasi status AKTIF, BERAKHIR, DICABUT, DISETUJUI, dan PENGOSONGAN untuk rumah dinas.
- Data ini cocok untuk mengetes menu master data, SIP, service, riwayat kondisi, laporan, export Excel, dan export PDF.
