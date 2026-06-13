PERBAIKAN NOTIFIKASI AKTIF DAN JUDUL LOGIN SIKARIS

Perubahan:
1. Tombol notifikasi di kanan atas sekarang dapat diklik.
2. Notifikasi menampilkan:
   - Usulan Penghapusan BMN baru dari satker untuk Admin System/Biro Umum.
   - Usulan PSP BMN baru dari satker untuk Admin System/Biro Umum.
   - Usulan Penghapusan/PSP yang perlu perbaikan untuk pemohon/satker.
   - SIP Kendaraan yang sudah habis atau akan habis dalam 30 hari.
   - SIP Rumah Negara yang sudah habis atau akan habis dalam 30 hari.
3. Setiap item notifikasi dapat diklik dan mengarah ke halaman detail terkait.
4. Halaman login sudah menggunakan judul/subtitle: Sistem Informasi Kendaraan dan Rumah Dinas.

Catatan teknis:
- Logika notifikasi ada di core/notifications.py.
- Data notifikasi dimasukkan ke seluruh template melalui core/context_processors.py.
- Tampilan dropdown notifikasi berada di templates/base.html.
- Jika belum muncul, lakukan hard refresh browser.
