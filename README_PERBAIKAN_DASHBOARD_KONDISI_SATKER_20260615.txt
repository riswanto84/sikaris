PERBAIKAN DASHBOARD KONDISI KENDARAAN & RUMAH NEGARA PER SATKER
=================================================================

Perubahan yang diterapkan:

1. Dashboard kendaraan sekarang menghitung kondisi aset secara fleksibel.
   Data lama/dummy yang tersimpan sebagai label "Baik", "Rusak Ringan",
   atau "Rusak Berat" tetap dihitung benar, tidak hanya kode database
   "BAIK", "RUSAK_RINGAN", dan "RUSAK_BERAT".

2. Dashboard tetap mengikuti cakupan satker/unit kerja user melalui field
   Unit Kerja/Satker pada Manajemen User. Untuk user Rehsos, data yang
   dihitung adalah data unit kerja Sekretariat Direktorat Jenderal
   Rehabilitasi Sosial.

3. Ditambahkan kartu ringkasan kondisi Rumah Negara:
   - Rumah Negara Baik
   - Rumah Negara Rusak Ringan
   - Rumah Negara Rusak Berat

4. Grafik Kondisi Rumah Negara mengikuti cakupan satker/unit kerja yang sama
   seperti grafik kendaraan.

5. Ditambahkan daftar "Rumah Negara Perlu Tindakan" pada dashboard, yaitu
   rumah negara yang kondisinya bukan Baik.

File yang diubah:
- core/views.py
- templates/core/dashboard.html

Catatan:
Perubahan ini tidak membutuhkan migrasi database karena hanya memperbaiki
logika query/perhitungan dashboard dan tampilan template.

Setelah ekstrak ZIP, jalankan:

python manage.py runserver

Jika menggunakan collectstatic di server production:

python manage.py collectstatic --noinput
