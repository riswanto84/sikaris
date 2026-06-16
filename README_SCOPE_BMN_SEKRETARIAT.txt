PERBAIKAN SCOPE ROLE BMN SEKRETARIAT KANTOR PUSAT
===================================================

Ketentuan yang diterapkan:
1. Admin System dan Biro Umum tetap dapat melihat semua satker/unit kerja.
2. Role Pengelola BMN pada Sekretariat kantor pusat Eselon I dapat melihat master data Pegawai, Kendaraan, Rumah Negara, dan dashboard untuk unit/direktorat di bawah Eselon I-nya.
   Contoh: user BMN dengan Unit Kerja "Sekretariat Direktorat Jenderal Rehabilitasi Sosial" dapat melihat data milik unit yang namanya mengandung "Rehabilitasi Sosial", seperti Direktorat Rehabilitasi Sosial Anak, Direktorat Rehabilitasi Sosial Lanjut Usia, dan seterusnya.
3. Role Pengelola BMN pada Sentra dan Balai tetap hanya bisa melihat data Pegawai, Kendaraan, Rumah Negara, dan dashboard milik Sentra/Balainya sendiri.
4. Filter dashboard kendaraan dan rumah negara memakai scope yang sama dengan master data.
5. Dropdown form Pegawai/Kendaraan/Rumah Negara ikut dibatasi sesuai scope tersebut.
6. Import master data untuk BMN Sekretariat kantor pusat boleh masuk ke unit yang masih berada dalam scope Eselon I-nya; untuk BMN Sentra/Balai tetap dipaksa ke unitnya sendiri.

File utama yang diubah:
- core/access.py
- core/views.py
- master/views.py

Catatan konfigurasi:
- Pastikan user BMN Sekretariat kantor pusat di menu Manajemen User memiliki Unit Kerja/Satker yang benar, misalnya:
  Sekretariat Direktorat Jenderal Rehabilitasi Sosial
- Pastikan data unit Direktorat di master Unit Kerja memakai nama yang mengandung bidang Eselon I-nya, misalnya:
  Direktorat Rehabilitasi Sosial Anak
  Direktorat Rehabilitasi Sosial Lanjut Usia
  Direktorat Rehabilitasi Sosial Penyandang Disabilitas
- Untuk Sentra/Balai, jenis_unit sebaiknya diisi SENTRA atau BALAI agar scope selalu hanya unit sendiri.

Perubahan ini tidak membutuhkan migrasi database.
