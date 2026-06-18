PERBAIKAN MASTER & SIP - 18 Juni 2026

Ringkasan perubahan:
1. Master Rumah Negara:
   - Tambah Nilai NJOP/m Tanah (editable).
   - Tahun Dibangun dihapus dari form.
   - Tambah Jumlah Lantai (tarikan SIMAN).
   - Tahun Perolehan diganti menjadi Tanggal Perolehan (tarikan SIMAN).
   - Tambah Kode Satker, Status Penggunaan SIMAN, dan Status Hukum.
   - Status Hukum dibatasi: Tidak ada sengketa / Sengketa.
   - Tombol hapus di list/detail Rumah Negara disembunyikan.
   - Field yang bisa diedit pada edit manual: daya listrik, latitude, longitude, jumlah kamar tidur, jumlah kamar mandi, NJOP/m tanah, sertifikat, dan foto.

2. Master Unit Kerja:
   - Tambah Kode Satker dari SIMAN (non-editable di form manual).
   - Jenis Unit dihilangkan dari form dan template import.
   - Tombol hapus Unit Kerja di list/detail disembunyikan.
   - Tambah role Anak Satker pada core.roles.

3. Master Kendaraan:
   - Kode Kendaraan diganti label menjadi Kode Register.
   - Tambah Kode Satker.
   - Tahun Perolehan diarahkan menjadi Tanggal Perolehan.
   - NUP diubah menjadi numerik (migration membersihkan NUP non angka menjadi kosong sebelum alter field).
   - Status Pemanfaatan ditampilkan sebagai Status Penggunaan.
   - Tambah status Dioperasionalkan Satker Lain.
   - Keterangan Status Pemanfaatan tetap tersedia.
   - Jenis Kendaraan mengikuti file Excel yang diupload.
   - Tombol hapus di list/detail Kendaraan disembunyikan.
   - Pada edit manual hanya bisa mengubah: Masa Berlaku STNK, Upload BPKB, Upload STNK, Jatuh Tempo Pajak. Field lainnya dikunci.

4. Import SIMAN/Master:
   - Import kendaraan dan rumah negara menggunakan update_or_create.
   - Data baru dibuat jika belum ada.
   - Data lama diperbarui jika ada perubahan pada file import.
   - Template import ditambah kode_register/kode_satker/tanggal_perolehan/status_penggunaan.

5. SIP:
   - Jenis Kendaraan pada pembuatan SIP tetap otomatis dari Master Kendaraan.
   - Tambah tombol Export SIP PDF/Excel/CSV pada SIP Kendaraan dan SIP Rumah Negara.
   - Tambah tampilan Status Aktif/Non Aktif SIP pada daftar SIP.
   - Detail SIP Kendaraan menampilkan Riwayat Service kendaraan terkait.

6. Dashboard & Notifikasi:
   - Tambah notifikasi pajak kendaraan yang akan jatuh tempo 30 hari ke depan.
   - Tambah kartu Dashboard: Pajak Kendaraan Akan Jatuh Tempo.

Catatan teknis:
- Jalankan migrasi: python manage.py migrate
- Environment container ini belum memiliki Django terinstall, sehingga validasi yang bisa dilakukan di sini adalah py_compile semua file Python.
