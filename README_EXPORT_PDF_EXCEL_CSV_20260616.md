# Perbaikan Export PDF, Excel, dan CSV SIKARIS

Perbaikan ini menambahkan tombol dan endpoint export untuk halaman daftar/transaksi yang menampilkan tabel data.

## Modul yang ditambahkan export

1. Transaksi SIP Kendaraan
2. Persetujuan SIP Kendaraan Kepala Biro Umum
3. Transaksi Service Kendaraan
4. Riwayat Kondisi Kendaraan
5. Transaksi SIP Rumah Negara
6. Persetujuan SIP Rumah Negara Sekjen
7. Permohonan Penghapusan BMN, termasuk mode Verifikasi Biro Umum, Penetapan Sekjen, dan Persetujuan Dirjen Rehsos
8. Permohonan PSP BMN, termasuk mode Verifikasi Biro Umum dan Penetapan Sekjen
9. Master Tanah Negara
10. Tabel administrasi: Manajemen User, Riwayat Login, Counter Kunjungan, dan Manajemen Role

Catatan: Master Unit Kerja, Pegawai, Kendaraan, dan Rumah Negara sebelumnya sudah memiliki export PDF/Excel/CSV dan tetap dipertahankan.

## File baru/diubah utama

- `core/export_utils.py`
- `kendaraan/views.py`, `kendaraan/urls.py`
- `rumah_dinas/views.py`, `rumah_dinas/urls.py`
- `penghapusan/views.py`, `penghapusan/urls.py`
- `psp/views.py`, `psp/urls.py`
- `tanah_negara/views.py`, `tanah_negara/urls.py`
- `accounts/views.py`, `accounts/urls.py`
- Template daftar terkait pada folder `templates/`
- `requirements.txt` dinormalisasi ke UTF-8 agar `pip install -r requirements.txt` tidak bermasalah.

## Perilaku export

Export mengikuti parameter pencarian `q` dan `search_field` yang sedang aktif pada halaman daftar, sehingga data yang diunduh sesuai hasil filter/pencarian yang tampil.

Format yang tersedia:

- PDF: format landscape untuk tabel lebar, maksimal 500 baris pertama agar file tidak terlalu berat.
- Excel: `.xlsx`, dengan header berwarna, auto-filter, freeze header, dan lebar kolom otomatis.
- CSV: `.csv` UTF-8 BOM agar mudah dibuka di Microsoft Excel.

## Cara menjalankan

```bash
pip install -r requirements.txt
python manage.py check
python manage.py runserver
```

