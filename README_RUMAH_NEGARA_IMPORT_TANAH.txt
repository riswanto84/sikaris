UPDATE FITUR SIKARIS - RUMAH NEGARA, IMPORT EXCEL/CSV, DAN TANAH NEGARA

Perubahan utama:
1. Seluruh label menu/tampilan Rumah Dinas diganti menjadi Rumah Negara.
   Nama model dan URL internal masih memakai rumah_dinas agar kompatibel dengan data lama.

2. Import Excel/CSV ditambahkan untuk:
   - Pegawai
   - Aset Kendaraan
   - Aset Rumah Negara
   - Tanah Negara

3. Form import memakai upload progress bar berbasis XMLHttpRequest.
   Progress bar menampilkan persentase upload file sehingga user tahu proses upload berjalan.
   Setelah upload 100%, server memproses data dan menampilkan ringkasan jumlah data baru/update/gagal.

4. Latitude dan longitude tetap dipertahankan pada Rumah Negara dan Tanah Negara.
   Field import yang dikenali: latitude/lat dan longitude/long/lng.

5. SIP Rumah Negara ditambahkan konsep:
   - Pemegang SIP
   - Penghuni Aktual
   Contoh: Pemegang SIP Kepala Biro Umum, tetapi penghuni aktual Saudari Samsiar.

6. SIP Rumah Negara ditambahkan data Sewa PNBP tahunan:
   - Status bayar PNBP: Sudah Bayar / Belum Bayar / Tidak Wajib
   - Tahun PNBP
   - Nilai sewa PNBP
   - Tanggal bayar PNBP
   - Bukti bayar PNBP

7. Fitur Tanah Negara ditambahkan dan bersifat rahasia.
   Untuk saat ini hanya Admin System/superuser yang bisa mengakses.
   Data tanah mencakup:
   - Kode tanah
   - Nama/lokasi tanah
   - Unit kerja/satker
   - Alamat dan wilayah
   - Latitude dan longitude
   - Luas tanah
   - NUP/kode barang/nilai perolehan
   - Nomor dan tanggal sertifikat
   - Status tanah: digunakan, idle, sengketa, disewakan/dimanfaatkan, lainnya
   - Digunakan oleh
   - Upload sertifikat PDF/gambar
   - Preview PDF/gambar sertifikat

8. Rumah Negara sekarang memiliki field Unit Kerja/Satker.
   Ini membuat pembatasan akses user unit kerja lebih tepat berdasarkan aset unitnya.

Cara menjalankan setelah extract:
cd sikaris
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver

Contoh header import pegawai:
nip, nik, nama, jabatan, pangkat, golongan, unit_kerja, no_hp, email, alamat, status_pegawai

Contoh header import kendaraan:
kode_kendaraan, nomor_polisi, merek, tipe, jenis_kendaraan, tahun_pembuatan, tahun_perolehan, warna, nomor_rangka, nomor_mesin, nomor_bpkb, nomor_stnk, masa_berlaku_stnk, jatuh_tempo_pajak, nup, kode_barang, nilai_perolehan, unit_kerja, pengguna_nip, kondisi, status_pemanfaatan, kilometer_terakhir

Contoh header import rumah negara:
kode_rumah, nama_rumah, jenis_rumah, unit_kerja, alamat, provinsi, kabupaten_kota, kecamatan, kelurahan, latitude, longitude, luas_tanah, luas_bangunan, nup, kode_barang, nilai_perolehan, nomor_sertifikat, status_tanah, kondisi, status_pemanfaatan

Contoh header import tanah negara:
kode_tanah, nama_tanah, unit_kerja, alamat, provinsi, kabupaten_kota, kecamatan, kelurahan, latitude, longitude, luas_tanah, nup, kode_barang, nilai_perolehan, nomor_sertifikat, tanggal_sertifikat, status_tanah, digunakan_oleh, keterangan
