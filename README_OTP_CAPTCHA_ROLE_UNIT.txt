SIKARIS - OTP EMAIL, CAPTCHA, DAN BATASAN AKSES UNIT KERJA
============================================================

1. FITUR LOGIN AMAN
-------------------
Login sekarang menggunakan 2 tahap:

Tahap 1:
- Username
- Password
- Captcha angka sederhana

Tahap 2:
- Kode OTP 6 digit dikirim ke email user
- OTP berlaku 5 menit
- Maksimal percobaan OTP 5 kali

Untuk lokal/development, EMAIL_BACKEND default memakai console:
- Kode OTP akan tampil di terminal tempat menjalankan `python manage.py runserver`

Untuk produksi, isi environment variable SMTP:
- EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
- EMAIL_HOST=smtp.gmail.com
- EMAIL_PORT=587
- EMAIL_USE_TLS=True
- EMAIL_HOST_USER=email_pengirim@gmail.com
- EMAIL_HOST_PASSWORD=app_password_email
- DEFAULT_FROM_EMAIL=email_pengirim@gmail.com

Catatan Gmail:
Gunakan App Password, bukan password Gmail biasa.


2. FILE YANG DITAMBAHKAN/DIUBAH
--------------------------------
Ditambahkan:
- accounts/forms.py
- accounts/views.py
- templates/accounts/verify_otp.html
- core/access.py
- README_OTP_CAPTCHA_ROLE_UNIT.txt

Diubah:
- accounts/urls.py
- templates/accounts/login.html
- sikaris/settings.py
- core/roles.py
- core/context_processors.py
- core/management/commands/seed_roles.py
- master/forms.py
- master/views.py
- kendaraan/forms.py
- kendaraan/views.py
- rumah_dinas/forms.py
- rumah_dinas/views.py
- laporan/views.py


3. ATURAN ROLE DAN UNIT KERJA
-----------------------------
User Biro Umum:
- Dapat melihat dan CRUD data semua satker/unit kerja.
- Terdeteksi sebagai Biro Umum jika:
  a. user adalah superuser; atau
  b. user masuk group "Biro Umum"; atau
  c. pegawai terkait user berada pada unit kerja yang namanya mengandung "Biro Umum".

User unit kerja lainnya:
- Hanya bisa melihat dan CRUD data pada unit kerjanya.
- Data dibatasi berdasarkan relasi unit kerja:
  - Pegawai: pegawai.unit_kerja
  - Kendaraan: kendaraan.unit_kerja
  - SIP Kendaraan: kendaraan.unit_kerja atau pegawai.unit_kerja
  - Service Kendaraan: kendaraan.unit_kerja
  - Riwayat Kondisi Kendaraan: kendaraan.unit_kerja
  - SIP Rumah Dinas: pegawai.unit_kerja
  - Rumah Dinas: rumah yang memiliki riwayat SIP pegawai dari unit kerja tersebut

Penting:
Agar pembatasan unit kerja berjalan, user harus terhubung dengan data pegawai.
Sistem mencocokkan user dengan pegawai melalui:
1. username user = NIP pegawai, atau
2. email user = email pegawai, atau
3. username user = email pegawai.

Jika user bukan Biro Umum dan belum cocok dengan pegawai/unit kerja, sistem akan menolak akses data unit.


4. PERINTAH SETUP
-----------------
Setelah extract ZIP:

cd sikaris
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver

Untuk data dummy:
python manage.py generate_dummy_data --jumlah 100 --clear


5. USER DEMO
------------
Setelah menjalankan seed_roles:

adminsystem / Password123! / Admin System / Superuser
biroumum    / Password123! / Biro Umum
bmn         / Password123! / Pengelola BMN
pemeliharaan/ Password123! / Pemeliharaan Kendaraan

Karena OTP memakai console backend saat lokal, lihat kode OTP di terminal runserver.


6. CATATAN RUMAH DINAS
----------------------
Model RumahDinas saat ini belum memiliki field unit_kerja langsung.
Karena itu pembatasan Rumah Dinas untuk user non-Biro Umum dilakukan melalui relasi SIP Rumah Dinas:
rumah_dinas -> SIPRumahDinas -> pegawai -> unit_kerja.

Jika di masa depan ingin rumah dinas benar-benar melekat pada satker tertentu, sebaiknya tambahkan field `unit_kerja` pada model RumahDinas.
