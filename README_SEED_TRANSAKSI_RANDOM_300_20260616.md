# Seed Data Random Transaksi SIKARIS

File ini menambahkan Django management command:

```bash
python manage.py seed_transaksi_random --count 300
```

Command tersebut membuat data dummy pada berbagai satker untuk jenis transaksi berikut:

1. SIP Kendaraan
2. Service Kendaraan
3. Riwayat Kondisi Kendaraan
4. SIP Rumah Negara
5. Perbaikan Rumah Negara
6. Permohonan Penghapusan BMN beserta detail barang
7. Permohonan PSP BMN beserta detail barang

Default `--count 300` berarti 300 data untuk masing-masing jenis transaksi utama di atas.

## Cara menjalankan

Pastikan migrasi sudah berjalan:

```bash
python manage.py migrate
```

Lalu jalankan:

```bash
python manage.py seed_transaksi_random --count 300
```

Jika ingin menghapus data dummy transaksi lama yang dibuat command ini lalu membuat ulang:

```bash
python manage.py seed_transaksi_random --count 300 --clear
```

Command ini juga otomatis menambahkan data master minimal apabila data master satker, pegawai, kendaraan, atau rumah negara belum cukup untuk membuat transaksi.

## Catatan

Data dummy ditandai dengan teks:

```text
DUMMY-SEED-SIKARIS
```

Tanda tersebut dipakai oleh opsi `--clear` agar tidak menghapus data asli/non-dummy.
