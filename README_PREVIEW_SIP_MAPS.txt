PERUBAHAN PREVIEW DOKUMEN SIP DAN GOOGLE MAPS

1. Halaman Detail SIP Kendaraan dan Detail SIP Rumah Negara sekarang menampilkan Preview Dokumen SIP jika field dokumen_sip berisi file PDF.
2. Jika dokumen SIP bukan PDF, sistem tetap menampilkan tombol/link untuk membuka dokumen.
3. Halaman Detail Rumah Negara otomatis menampilkan Preview Google Maps jika data rumah negara memiliki latitude dan longitude.
4. Preview Maps menggunakan koordinat latitude/longitude yang tersimpan pada data Rumah Negara.
5. Perubahan diterapkan pada core/detail.py dan templates/includes/generic_detail.html sehingga berlaku otomatis untuk halaman detail berbasis GenericDetailMixin.

Catatan:
- Agar preview PDF tampil, file SIP harus diupload pada field Dokumen SIP.
- Agar Google Maps tampil, field latitude dan longitude harus terisi.
- Jika preview belum berubah, lakukan hard refresh browser: Cmd+Shift+R untuk Mac atau Ctrl+F5 untuk Windows.
