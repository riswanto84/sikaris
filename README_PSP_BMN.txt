FITUR PERMOHONAN PSP BMN - SIKARIS
==================================

Menu baru:
- PSP BMN -> Permohonan PSP
- URL: /psp-bmn/

Alur umum:
1. Unit kerja mengajukan permohonan Penetapan Status Penggunaan (PSP) BMN.
2. Unit kerja memilih jenis barang/aset: Kendaraan, Rumah Negara, Tanah Negara, atau BMN Lainnya.
3. Unit kerja mengunggah dokumen dasar PSP.
4. Biro Umum memverifikasi kelengkapan dokumen, memberi catatan, dan menetapkan status permohonan.
5. Jika disetujui, Biro Umum dapat mengisi nomor/tanggal penetapan PSP dan mengunggah dokumen penetapan PSP.

Dokumen dasar yang wajib untuk seluruh pengajuan PSP:
- Surat permohonan dari Satker.
- Surat pengantar/usulan dari Eselon I.
- Daftar kondisi barang.
- Laporan sub kelompok barang.
- Surat Pernyataan Kepala Satker.

Validasi khusus:
- Jika jenis barang = Kendaraan dan nilai PSP > Rp100.000.000, maka sistem mewajibkan:
  1. Foto kendaraan; dan
  2. Dokumen kepemilikan kendaraan seperti BPKB/STNK/dokumen lain, ATAU Surat Pernyataan Kepala Satker sebagai pengganti bila dokumen kepemilikan tidak tersedia.

Akses:
- Biro Umum / superuser: melihat dan memproses semua permohonan dari seluruh unit kerja.
- User unit kerja: hanya melihat, mengajukan, mengedit, dan menghapus permohonan unit kerjanya sendiri selama belum diproses lanjut Biro Umum.

Perintah setelah extract ZIP:
python manage.py migrate
python manage.py seed_roles
python manage.py runserver

Jika memakai Mac dan command python tidak ada:
python3 manage.py migrate
python3 manage.py seed_roles
python3 manage.py runserver
