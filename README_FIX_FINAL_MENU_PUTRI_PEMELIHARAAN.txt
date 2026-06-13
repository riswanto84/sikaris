PERBAIKAN FINAL MENU ROLE PEMELIHARAAN KENDARAAN

Masalah:
User Putri dengan role Pemeliharaan Kendaraan masih melihat menu Pegawai, Rumah Negara, Unit Kerja,
SIP Rumah Negara, Penghapusan BMN, PSP BMN, dan Export Rumah Negara.

Penyebab yang ditemukan:
Pada versi sebelumnya user Pemeliharaan yang unit kerjanya terbaca sebagai Biro Umum tidak masuk mode restricted,
sehingga sidebar masih menampilkan menu penuh.

Perbaikan:
1. is_pemeliharaan_strict sekarang TRUE untuk setiap user yang memiliki role Pemeliharaan Kendaraan,
   kecuali superuser/Admin System.
2. Role Pemeliharaan tetap dibatasi walaupun unit kerjanya mengandung kata Biro Umum.
3. Sidebar untuk Pemeliharaan hanya menampilkan:
   - Dashboard
   - Daftar Kendaraan
   - Service Kendaraan
   - Laporan Kendaraan
4. Export Laporan Rumah Negara disembunyikan untuk Pemeliharaan.

File yang diubah:
- core/context_processors.py
- templates/base.html
- templates/laporan/index.html
- core/management/commands/cek_role_user.py

Setelah update:
1. Jalankan server ulang.
2. Logout user Putri.
3. Login ulang.
4. Hard refresh browser: Cmd+Shift+R / Ctrl+F5.

Cek role lewat terminal:
python3 manage.py cek_role_user Putri

Jika username huruf kecil:
python3 manage.py cek_role_user putri

Hasil yang benar harus menampilkan:
is_pemeliharaan_kendaraan: True
is_pemeliharaan_strict: True
