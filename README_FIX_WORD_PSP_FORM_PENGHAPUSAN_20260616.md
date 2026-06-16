# Perbaikan Word PSP dan Form Penghapusan BMN - 2026-06-16

## Perbaikan Dokumen Word PSP
- Generate dokumen PSP tetap memakai format Word (.docx) agar bisa diedit sebelum TTE BSrE/e-Meterai.
- Kop surat Word PSP dirapikan mengikuti contoh dokumen Biro Umum:
  - logo Kemensos di kiri atas;
  - teks Kementerian/Sekretariat Jenderal/Biro Umum di tengah;
  - garis bawah kop;
  - margin dan ukuran font diperkecil agar tidak melebar/terpotong.
- Tabel metadata Yth/Dari/Hal/Lampiran/Sifat/Tanggal dibuat tanpa border dan lebih rapi.
- Blok tanda tangan diposisikan di kanan bawah dengan ruang TTE/e-Meterai yang tidak saling menimpa.
- Nama dan NIP pejabat tetap dikosongkan jika belum diisi eksplisit agar tidak salah mengambil data dummy.

## Perbaikan Form Permohonan Penghapusan BMN
Field berikut dihapus dari form input/edit Permohonan Penghapusan BMN:
- Jenis Aset
- Kendaraan
- Rumah Negara
- Tanah Negara
- Kode Barang

Catatan:
- Field tersebut tidak dihapus dari database agar data lama tetap aman.
- Untuk penghapusan banyak barang, detail barang tetap diakomodir melalui fitur Import Excel Barang Penghapusan.
- Jika jenis aset tidak diisi dari form, sistem otomatis menyimpan nilai default `LAINNYA`.

## Cara Menjalankan
Tidak ada migrasi database baru.

```bash
python3 manage.py runserver
```
