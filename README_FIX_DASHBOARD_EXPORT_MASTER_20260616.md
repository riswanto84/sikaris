# Perbaikan Dashboard dan Export Master Data

Perubahan:

1. Card dashboard berikut dihapus:
   - Menunggu TTE
   - Menunggu e-Meterai

2. Counter context dashboard terkait TTE/e-Meterai PSP yang tidak dipakai juga dihapus.

3. Pada master data ditambahkan fitur export:
   - Export PDF
   - Export Excel (.xlsx)
   - Export CSV

4. Export mengikuti scope/hak akses user dan mengikuti filter pencarian yang sedang digunakan pada daftar.

Menu yang ditambahkan export:
- Master Pegawai
- Master Kendaraan
- Master Rumah Negara
- Master Unit Kerja

Tidak ada perubahan struktur database, sehingga tidak perlu migrate.
