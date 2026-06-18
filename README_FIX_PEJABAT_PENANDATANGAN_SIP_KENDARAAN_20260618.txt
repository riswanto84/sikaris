Perbaikan Pejabat Penandatangan SIP Kendaraan - 18 Juni 2026

Perubahan:
1. Menambahkan field baru pada Master Kendaraan:
   - pejabat_penandatangan_sip
   - Relasi ke Master Pegawai
   - Digunakan sebagai sumber pejabat penerbit/penandatangan SIP Kendaraan.

2. Form SIP Kendaraan:
   - Menampilkan field readonly:
     Pejabat Penandatangan SIP Kendaraan (otomatis dari Master Kendaraan)
   - Field otomatis ikut berubah saat dropdown Kendaraan dipilih.

3. Generate PDF SIP Kendaraan:
   - Nama, NIP, dan jabatan pejabat penandatangan diambil dari Master Kendaraan.
   - Jika data Master Kendaraan belum memiliki pejabat penandatangan, fallback lama dari Master Unit Kerja tetap dipakai.

4. Migration baru:
   - master/migrations/0013_kendaraan_pejabat_penandatangan_sip.py

Setelah ekstrak ZIP jalankan:
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

Catatan:
Lengkapi terlebih dahulu field Pejabat Penandatangan SIP Kendaraan pada Master Kendaraan agar nama pejabat muncul pada preview PDF SIP.
