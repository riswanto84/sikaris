UPDATE DATA DUMMY - VARIASI JENIS KENDARAAN
===========================================

Perbaikan ini menambahkan variasi jenis kendaraan pada data dummy, yaitu:

1. Mobil
2. Sepeda Motor
3. Motor Roda 3
4. Kendaraan Lainnya

File yang diubah:
- core/constants.py
- core/management/commands/generate_dummy_data.py
- db.sqlite3 sudah di-generate ulang dengan 100 data dummy terbaru

Komposisi 100 kendaraan dummy:
- Mobil: 30 data
- Sepeda Motor: 30 data
- Motor Roda 3: 20 data
- Kendaraan Lainnya: 20 data

Cara inject/generate ulang data dummy:

1. Masuk ke folder project:
   cd sikaris

2. Jalankan migrasi:
   python manage.py migrate

3. Generate ulang data dummy 100 data:
   python manage.py generate_dummy_data --jumlah 100 --clear

Opsi --clear hanya menghapus data dummy dengan prefix DMY, sehingga data asli non-dummy tidak ikut terhapus.
