Perbaikan tombol Edit pada Daftar SIP Kendaraan

Perubahan:
1. Tombol Edit pada Daftar SIP Kendaraan sekarang tampil untuk status:
   - DRAFT
   - DIAJUKAN
   - DITOLAK
   - TERBIT
2. Form edit SIP Kendaraan juga diizinkan untuk status TERBIT bagi user berwenang.
3. Tidak ada perubahan database, sehingga tidak perlu makemigrations.

Setelah ekstrak ZIP, cukup restart server Django.
