PERBAIKAN SIKARIS - RIWAYAT LOGIN, COUNTER KUNJUNGAN, DAN PREVIEW KUITANSI SERVICE

Perubahan:
1. Menambahkan riwayat login user.
   - Dicatat otomatis setiap user berhasil login.
   - Data yang dicatat: user, waktu login, IP address, user agent/perangkat, session key.
   - Menu hanya tampil untuk Admin System: Pengaturan > Riwayat Login.

2. Menambahkan counter kunjungan user.
   - Menghitung jumlah kunjungan halaman aplikasi oleh user yang sudah login.
   - Data yang dicatat: total kunjungan, waktu kunjungan terakhir, halaman terakhir, IP terakhir, user agent terakhir.
   - Menu hanya tampil untuk Admin System: Pengaturan > Counter Kunjungan.
   - Pada Manajemen User ditambahkan kolom Total Kunjungan.

3. Menampilkan bukti kuitansi pada Detail Service Kendaraan.
   - Bukti kuitansi PDF ditampilkan sebagai preview PDF di bawah halaman detail.
   - Bukti kuitansi gambar ditampilkan sebagai preview gambar.
   - Tersedia tombol Buka File.

File yang ditambahkan/diubah:
- accounts/models.py
- accounts/migrations/0002_loginhistory_uservisitcounter.py
- accounts/signals.py
- accounts/middleware.py
- accounts/apps.py
- accounts/views.py
- accounts/urls.py
- templates/accounts/login_history_list.html
- templates/accounts/visit_counter_list.html
- templates/accounts/user_list.html
- templates/base.html
- kendaraan/views.py
- templates/includes/generic_detail.html
- sikaris/settings.py

Cara menjalankan setelah extract:
cd sikaris
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver

Jika di Mac perintah python tidak dikenali, gunakan:
python3 manage.py migrate
python3 manage.py seed_roles
python3 manage.py runserver

Catatan:
- Counter kunjungan mulai bertambah setelah user membuka halaman aplikasi setelah fitur ini aktif.
- Riwayat login mulai tercatat setelah user login setelah fitur ini aktif.
