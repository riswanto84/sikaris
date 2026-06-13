PERUBAHAN: Tombol Hapus untuk Semua Fitur List SIKARIS

Perubahan yang ditambahkan:
1. Tombol Hapus ditambahkan di sebelah tombol Edit pada halaman list:
   - Unit Kerja
   - Pegawai
   - Kendaraan
   - Rumah Negara
   - SIP Kendaraan
   - Service Kendaraan
   - Riwayat Kondisi Kendaraan
   - SIP Rumah Negara
   - Tanah Negara

2. Fitur Manajemen User dan Role sudah memiliki tombol Hapus dari versi sebelumnya dan tetap dipertahankan.

3. Semua tombol hapus diarahkan ke halaman konfirmasi sebelum data dihapus.
   Data tidak langsung terhapus dari halaman list.

4. Hak akses tetap mengikuti aturan aplikasi:
   - Biro Umum / superuser dapat menghapus data semua unit kerja.
   - User unit kerja hanya dapat menghapus data sesuai unit kerjanya, selama role-nya berhak melakukan CRUD.
   - Tanah Negara tetap hanya untuk Admin System / superuser.

5. Jika data masih digunakan oleh relasi lain, aplikasi akan menampilkan pesan bahwa data tidak dapat dihapus.

Catatan teknis:
- Ditambahkan template includes/confirm_delete.html.
- Ditambahkan DeleteView pada master, kendaraan, rumah_dinas, dan tanah_negara.
- Perbaikan import Excel/CSV juga dipertahankan: BaseImportView dan TanahNegaraImportView memakai FormView agar tidak error instance.
