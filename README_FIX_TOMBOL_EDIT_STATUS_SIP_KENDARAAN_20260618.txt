Perbaikan tombol Edit pada daftar/detail SIP Kendaraan

Perubahan:
1. Tombol Edit ditambahkan pada Daftar SIP Kendaraan untuk status:
   - DRAFT
   - DIAJUKAN
   - TERBIT
2. Tombol Edit pada detail SIP Kendaraan juga mengikuti status tersebut.
3. Kolom Status Aktif tetap disembunyikan untuk role Pengelola BMN sesuai perbaikan sebelumnya.
4. Tombol Teruskan tetap menggunakan label 'Teruskan'.

Tidak ada perubahan database, sehingga tidak perlu makemigrations.
Cukup restart server Django setelah file diekstrak.
