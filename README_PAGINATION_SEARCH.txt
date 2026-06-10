FITUR PAGINATION DAN PENCARIAN LIST DATA SIKARIS
================================================

Perubahan yang ditambahkan:

1. Semua halaman list data sekarang menggunakan pagination server-side:
   - Master Unit Kerja
   - Master Pegawai
   - Master Kendaraan
   - Master Rumah Dinas
   - SIP Kendaraan
   - Service Kendaraan
   - Riwayat Kondisi Kendaraan
   - SIP Rumah Dinas

2. Semua halaman list data sekarang memiliki pencarian server-side:
   - Input kata kunci pencarian.
   - Dropdown pilihan field pencarian.
   - Pilihan "Semua Field" untuk mencari di seluruh field yang relevan.
   - Tombol Reset untuk menghapus filter.

3. Pencarian sudah mencakup field relasi terkait, misalnya:
   - Kendaraan bisa dicari berdasarkan unit kerja dan nama/NIP pengguna.
   - SIP Kendaraan bisa dicari berdasarkan nomor polisi, merek kendaraan, nama pegawai, NIP, jabatan, dan unit kerja pegawai.
   - Service/Riwayat Kondisi bisa dicari berdasarkan nomor polisi, merek, tipe, unit kerja, bengkel, uraian, kondisi, dan petugas.
   - SIP Rumah Dinas bisa dicari berdasarkan kode rumah, nama rumah, alamat, nama pegawai, NIP, jabatan, unit kerja, status, dan catatan.

4. File baru:
   - core/listing.py
   - templates/includes/list_search.html
   - templates/includes/pagination.html

5. File yang diubah:
   - master/views.py
   - kendaraan/views.py
   - rumah_dinas/views.py
   - templates/base.html
   - templates/master/unitkerja_list.html
   - templates/master/pegawai_list.html
   - templates/master/kendaraan_list.html
   - templates/master/rumah_list.html
   - templates/kendaraan/sip_list.html
   - templates/kendaraan/service_list.html
   - templates/kendaraan/kondisi_list.html
   - templates/rumah_dinas/sip_list.html

Cara menjalankan:

1. Extract ZIP.
2. Masuk folder project:
   cd sikaris
3. Jalankan:
   python manage.py migrate
   python manage.py runserver

Catatan:
- Pagination default 15 data per halaman.
- Parameter pencarian menggunakan q dan search_field di URL.
- Saat pindah halaman, filter pencarian tetap dipertahankan.
