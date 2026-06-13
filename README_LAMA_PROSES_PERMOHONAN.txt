FITUR LAMA PROSES PERMOHONAN - SIKARIS
======================================

Modul yang diperbarui:
1. Permohonan Penghapusan BMN
2. Permohonan PSP BMN

Tujuan:
- Menampilkan lama waktu proses pengajuan dari Satker/Unit Kerja ke Biro Umum.
- Menjadi pengingat bagi pemohon/Satker dan verifikator Biro Umum agar permohonan tidak tertunda.

Perubahan tampilan:
- Pada halaman daftar permohonan ditambahkan kolom: Lama Proses/Pengingat.
- Pada halaman detail ditambahkan kartu Lama Proses dan pesan pengingat.

Logika pengingat:
1. Status DIAJUKAN:
   - < 3 hari: Menunggu verifikasi Biro Umum.
   - 3 s.d. 6 hari: Perlu segera diverifikasi.
   - >= 7 hari: Terlambat diverifikasi.

2. Status PERLU_PERBAIKAN:
   - Pengingat ditujukan ke pemohon/Satker agar segera memperbaiki dokumen.

3. Status DIVERIFIKASI/DISETUJUI/PROSES:
   - >= 7 hari: Perlu tindak lanjut.
   - >= 14 hari: Proses melewati batas pantau.

4. Status SELESAI/DITOLAK:
   - Ditandai selesai.

Catatan teknis:
- Fitur ini menggunakan property Python pada model, sehingga tidak memerlukan migration database baru.
- Lama proses dihitung dari tanggal_permohonan sampai tanggal proses terakhir atau tanggal hari ini.
- File yang diubah:
  a. penghapusan/models.py
  b. psp/models.py
  c. templates/penghapusan/list.html
  d. templates/penghapusan/detail.html
  e. templates/psp/list.html
  f. templates/psp/detail.html
  g. static/css/app.css
  h. templates/base.html

Cara menjalankan:
python manage.py migrate
python manage.py seed_roles
python manage.py runserver
