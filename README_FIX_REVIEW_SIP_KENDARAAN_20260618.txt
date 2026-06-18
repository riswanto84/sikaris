PERBAIKAN SIP KENDARAAN - 18/06/2026

Perubahan:
1. Kolom Status Aktif/Non Aktif pada Daftar SIP Kendaraan disembunyikan untuk role Pengelola BMN.
2. Tombol "Teruskan ke Pejabat Penerbit" pada Daftar SIP Kendaraan diubah menjadi "Teruskan".
3. Tombol "Ajukan ke ..." pada Detail SIP Kendaraan juga diubah menjadi "Teruskan".
4. Pada halaman Review/Persetujuan Pejabat Penerbit SIP Kendaraan ditambahkan panel Review Persetujuan SIP Kendaraan.
5. Pejabat penerbit/Kepala Unit Kerja/Satker dapat:
   - Setujui dengan Keterangan Persetujuan.
   - Tolak dengan Alasan Penolakan wajib dan Keterangan Tambahan.
6. Keterangan persetujuan disimpan ke field catatan.
7. Alasan dan keterangan penolakan disimpan ke field catatan_penolakan.

Tidak ada perubahan struktur database, sehingga tidak perlu makemigrations.
Setelah ekstrak, cukup restart server Django.
