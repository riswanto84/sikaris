Perbaikan UI SIM Pengelolaan BMN - 2026-06-19

Perubahan:
1. Nama aplikasi pada base template dan login diubah menjadi SIM PENGELOLAAN BMN.
2. Logo Kementerian Sosial tetap dipertahankan pada sidebar dan halaman login.
3. Sidebar diperbarui menjadi tampilan modern Kemensos dengan section yang lebih rapi.
4. Login template dibuat ulang dengan layout dua panel, branding Kemensos, dan nama aplikasi baru.
5. CSS override baru ditambahkan pada static/css/sim_bmn_theme.css dan staticfiles/css/sim_bmn_theme.css.
6. Template lain yang memunculkan nama lama SIKARIS diubah menjadi SIM Pengelolaan BMN.

Catatan teknis:
- Tidak ada perubahan database.
- Tidak perlu makemigrations/migrate.
- Setelah ekstrak ZIP, restart server Django.
- Jika menggunakan collectstatic di production, jalankan python manage.py collectstatic.
