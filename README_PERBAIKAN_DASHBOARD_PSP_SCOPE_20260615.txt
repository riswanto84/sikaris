PERBAIKAN DASHBOARD PSP BMN SESUAI KEWENANGAN ROLE
Tanggal: 15 Juni 2026

Perubahan:
1. Dashboard menampilkan data PSP BMN sesuai kewenangan masing-masing role:
   - Total Permohonan PSP
   - PSP Dalam Proses
   - PSP Perlu Perbaikan
   - PSP Selesai / SK Terbit
   - Ringkasan Diajukan, Dalam Proses, Perlu Perbaikan, Selesai/SK Terbit
   - Status dokumen PSP yang menunggu TTE
   - Status dokumen PSP yang menunggu e-Meterai
   - Daftar PSP Perlu Tindak Lanjut

2. Scope PSP mengikuti aturan BMN yang sama dengan dashboard/master data:
   - Admin System / Biro Umum: semua satker/unit kerja.
   - Pengelola BMN Sekretariat kantor pusat Eselon I: Sekretariat + Direktorat di bawah Eselon I-nya.
   - Pengelola BMN Sentra/Balai: hanya data PSP pada Sentra/Balai miliknya sendiri.

3. List Permohonan PSP dan notifikasi PSP juga disesuaikan agar konsisten dengan scope dashboard.

File yang diubah:
- core/access.py
- core/views.py
- core/notifications.py
- psp/views.py
- templates/core/dashboard.html

Tidak perlu makemigrations/migrate karena tidak ada perubahan struktur database.
Setelah ekstrak cukup jalankan:
python manage.py runserver
