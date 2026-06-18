Perbaikan tombol Teruskan ke Pejabat Penerbit - SIP Kendaraan

Perubahan:
1. Menu Daftar SIP Kendaraan sekarang menampilkan tombol "Teruskan ke Pejabat Penerbit" pada baris SIP berstatus DRAFT/DITOLAK.
2. Tombol tersedia untuk user yang berwenang mengelola SIP, termasuk Pengelola BMN dan Admin System.
3. Tombol melakukan POST ke endpoint yang sudah ada: kendaraan:sip_ajukan_kabiro.
4. Label pada halaman Detail SIP Kendaraan juga diubah menjadi "Teruskan ke Pejabat Penerbit" agar konsisten.
5. Tidak ada perubahan database dan tidak perlu makemigrations.

Catatan:
- SIP tetap harus memiliki konsep PDF terlebih dahulu. Jika belum ada konsep PDF, sistem akan menampilkan pesan agar Generate Konsep PDF dilakukan lebih dulu.
- Setelah diteruskan, status SIP menjadi DIAJUKAN dan akan muncul di menu Persetujuan Pejabat Penerbit SIP Kendaraan.
