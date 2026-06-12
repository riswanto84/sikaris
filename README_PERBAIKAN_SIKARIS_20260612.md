# Perbaikan SIKARIS 12 Juni 2026

Perbaikan yang diterapkan:

1. Detail kendaraan menampilkan foto utama/galeri foto kendaraan.
2. Notifikasi kanan atas dihilangkan dari topbar karena belum memiliki fungsi klik.
3. Username kanan atas menjadi menu profile dengan akses Edit Profile, Ubah Kata Sandi, dan Logout.
4. Status pemanfaatan kendaraan ditambah: Tidak Diketahui Keberadaannya dan Dikuasai Pihak Lain, serta field keterangan status pemanfaatan.
5. Status rumah negara ditambah: Dalam Penguasaan Pihak Lain, serta field keterangan status pemanfaatan.
6. Subtitle logo SIKARIS dikembalikan menjadi Sistem Informasi Kendaraan dan Rumah Dinas.
7. Detail SIP Rumah Negara menampilkan foto rumah, latitude, longitude, dan preview Google Maps dari master Rumah Negara.
8. Form service kendaraan tidak lagi meminta input total biaya. Total biaya otomatis dihitung dari biaya jasa + biaya sparepart.
9. Menu Riwayat Kondisi di Pemeliharaan Kendaraan dihilangkan dari sidebar.
10. Permohonan Penghapusan BMN: dokumen usulan dan dokumen pendukung dibatasi PDF; foto kondisi aset bisa upload multi foto.
11. Permohonan PSP BMN disederhanakan: tidak lagi menampilkan field kendaraan, rumah negara, tanah negara, kode barang, NUP, nama barang, kondisi barang, dan lokasi barang. Dokumen persyaratan dasar digabung menjadi satu file PDF. Foto kendaraan diganti menjadi Foto Barang multi foto. Nomor Penetapan PSP diganti menjadi Nomor SK PSP dan Dokumen Penetapan PSP menjadi SK Penetapan PSP.

Setelah extract ZIP, jalankan:

```bash
cd sikaris
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver
```

Jika menggunakan Mac dan command `python` tidak tersedia, gunakan `python3`.
