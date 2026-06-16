PERBAIKAN SCOPE PENGELOLA BMN ESELON I - 2026-06-15

Perubahan:
1. Pengelola BMN tidak lagi memakai akses global hanya karena unitnya Biro Umum.
2. Pengelola BMN Biro Umum dibatasi pada data unit di bawah Sekretariat Jenderal.
3. Pengelola BMN pada Ditjen/Itjen/Badan kantor pusat dibatasi pada data unit di bawah Eselon I masing-masing.
4. Pengelola BMN Sentra/Balai tetap hanya melihat dan CRUD data pada Sentra/Balai masing-masing.
5. Scope dashboard disamakan dengan scope master/transaksi.
6. Dashboard ditambahkan kartu Total Pegawai.
7. Form PSP dan Penghapusan BMN ikut dibatasi pilihan Unit/Pegawai/Barang sesuai scope Eselon I pengguna.

Catatan:
- Tidak perlu migrasi database.
- Perubahan utama ada di core/access.py, core/dashboard.html, psp/forms.py, psp/views.py, penghapusan/forms.py, dan penghapusan/views.py.
