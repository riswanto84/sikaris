PERBAIKAN DROPDOWN SEARCHABLE

Fitur yang ditambahkan:
1. Semua field dropdown pada form Django diberi class searchable-select.
2. Dropdown berubah menjadi input pencarian tanpa library/CDN tambahan.
3. User bisa mengetik nama pegawai, NIP, unit kerja, kendaraan, rumah dinas, status, kondisi, dan pilihan lain.
4. Nilai asli tetap dikirim melalui elemen <select>, sehingga proses simpan data Django tetap berjalan normal.

File yang diubah:
- master/forms.py
- kendaraan/forms.py
- rumah_dinas/forms.py
- templates/base.html
- static/js/app.js
- staticfiles/js/app.js

Catatan:
Jika tampilan belum berubah, lakukan hard refresh browser:
- Mac: Cmd + Shift + R
- Windows: Ctrl + F5
