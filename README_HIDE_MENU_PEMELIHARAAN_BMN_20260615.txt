Perbaikan menu Pemeliharaan Kendaraan untuk role Pengelola BMN

Perubahan:
1. Menu Pemeliharaan Kendaraan / Service Kendaraan tidak lagi tampil untuk role Pengelola BMN.
2. Akses langsung ke URL Service Kendaraan dibatasi hanya untuk Admin System dan role Pemeliharaan Kendaraan.
3. Pengelola BMN tetap dapat mengelola master data dan transaksi lain sesuai scope unit/eselon I yang sudah diterapkan.

Tidak memerlukan migrasi database.
Jalankan: python3 manage.py runserver
