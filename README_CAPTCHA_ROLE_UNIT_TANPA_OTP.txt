SIKARIS - Login Captcha Tanpa OTP dan Role Unit Kerja
=====================================================

Perubahan versi ini:

1. OTP email DINONAKTIFKAN
   - Login tidak lagi mengirim OTP ke email.
   - User langsung masuk setelah username, password, dan captcha benar.
   - Konfigurasi SMTP/email tidak diperlukan untuk login.

2. Captcha tetap aktif
   - Login memakai captcha angka sederhana.
   - Contoh: 2 + 9 = ?
   - Captcha berubah setiap halaman login dibuka ulang atau login gagal.

3. Aturan akses role dan unit kerja tetap dipertahankan
   - Superuser dan user Biro Umum dapat melihat serta CRUD seluruh data semua satker/unit kerja.
   - User unit kerja lain hanya dapat melihat serta CRUD data pada unit kerjanya.
   - Pencocokan unit kerja user dilakukan melalui data Pegawai:
     a. username user = NIP pegawai, atau
     b. email user = email pegawai, atau
     c. username user = email pegawai.

4. Cara menjalankan

   cd sikaris
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_roles
   python manage.py runserver

5. Catatan
   - File templates/accounts/verify_otp.html masih boleh ada di folder template, tetapi tidak digunakan lagi karena URL OTP sudah dihapus.
   - Pengaturan email di settings.py boleh dibiarkan, karena tidak dipakai untuk login versi ini.
