Perbaikan Detail SIP Kendaraan - Pengelola BMN

Tanggal: 16 Juni 2026

Perubahan:
1. Detail SIP Kendaraan untuk role Pengelola BMN tetap dapat dibuka.
2. Tombol Edit tetap tampil untuk SIP Kendaraan status DRAFT atau DITOLAK.
3. Tombol Hapus tetap tampil untuk SIP Kendaraan status DRAFT atau DITOLAK.
4. Tombol Generate Konsep PDF tetap tampil untuk Pengelola BMN pada status DRAFT, DITOLAK, atau DIAJUKAN.
5. Generate Konsep PDF untuk Pengelola BMN diproteksi agar hanya bisa untuk data yang belum final.
6. Upload PDF TTE BSrE tetap hanya untuk pejabat penerbit SIP Kendaraan.

Catatan:
- Tidak ada migrasi database.
- Jalankan: python3 manage.py runserver
