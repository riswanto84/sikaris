Perbaikan tombol Edit pada Daftar SIP Kendaraan

Perubahan:
1. Menambahkan tombol Edit pada kolom Aksi Daftar SIP Kendaraan untuk status Draft/Konsep, Diajukan, dan Ditolak.
2. Tombol Teruskan tetap hanya muncul untuk status Draft/Konsep dan Ditolak.
3. Form Edit SIP Kendaraan sekarang dapat dibuka untuk status Diajukan agar Pengelola BMN/Admin dapat memperbaiki data sebelum proses persetujuan selesai.
4. Validasi form disesuaikan: status yang boleh diedit adalah DRAFT, DIAJUKAN, dan DITOLAK; status final seperti TERBIT tetap tidak dapat diedit.

Tidak ada perubahan database, sehingga tidak perlu makemigrations.
Cukup ekstrak ZIP dan restart server Django.
