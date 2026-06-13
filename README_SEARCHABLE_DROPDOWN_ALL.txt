PERBAIKAN SEARCHABLE DROPDOWN SIKARIS
=====================================

Perubahan:
1. Semua elemen <select> pada aplikasi otomatis menjadi searchable/dropdown dengan kolom pencarian.
2. Berlaku untuk form master dan transaksi, antara lain:
   - SIP Kendaraan
   - SIP Rumah Negara
   - Service Kendaraan
   - Riwayat Kondisi
   - Permohonan PSP BMN
   - Permohonan Penghapusan BMN
   - Tanah Negara
   - Manajemen User/Role dan form lain yang memakai dropdown
3. Tidak memakai CDN/library internet, sehingga tetap bisa berjalan offline di localhost.
4. Select asli tetap dipakai untuk submit data Django, sehingga tidak mengubah struktur backend/database.
5. Jika ingin mengecualikan dropdown tertentu, tambahkan atribut data-no-search="true" atau class "no-searchable" pada select.

File yang diubah:
- static/js/app.js
- static/css/app.css
- staticfiles/js/app.js
- staticfiles/css/app.css
- templates/base.html

Jika perubahan belum terlihat:
- Hard refresh browser: Cmd + Shift + R di Mac atau Ctrl + F5 di Windows.
- Jika deploy production, jalankan: python manage.py collectstatic --noinput
