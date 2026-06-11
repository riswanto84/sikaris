UPDATE FITUR MANAJEMEN USER DAN ROLE - SIKARIS
================================================

Perubahan yang ditambahkan:

1. Menu Django Admin di sidebar dihapus untuk semua role.
   - URL /admin/ tetap tidak ditampilkan pada menu aplikasi.
   - Pengelolaan user dan role sekarang dilakukan melalui menu internal SIKARIS.

2. Menu baru untuk Admin System:
   - Pengaturan > Manajemen User
   - Pengaturan > Manajemen Role

3. Manajemen User:
   - Tambah user
   - Edit user
   - Hapus user
   - Atur email, nama, status aktif, staff status, superuser
   - Atur role/group user
   - Ubah password user secara opsional pada halaman edit

4. Manajemen Role:
   - Tambah role
   - Edit role
   - Hapus role tambahan
   - Role bawaan sistem dilindungi agar tidak terhapus:
     * Admin System
     * Biro Umum
     * Pengelola BMN
     * Pemeliharaan Kendaraan

5. Aturan akses tetap dipertahankan:
   - Biro Umum / superuser dapat melihat dan CRUD semua data seluruh satker/unit kerja.
   - User unit kerja lain hanya dapat melihat dan CRUD data pada unit kerjanya.

Catatan penting untuk user unit kerja:
- Agar pembatasan data per unit kerja berjalan otomatis, buat user dengan salah satu pola berikut:
  1. username user sama dengan NIP pegawai; atau
  2. email user sama dengan email pegawai; atau
  3. username user sama dengan email pegawai.

Cara menjalankan setelah extract ZIP:

cd sikaris
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver

Login sebagai admin system/biro umum lalu buka menu:
Pengaturan > Manajemen User
Pengaturan > Manajemen Role
