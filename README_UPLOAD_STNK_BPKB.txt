# Fitur Upload STNK dan BPKB Kendaraan

Perubahan yang ditambahkan:

1. Master Kendaraan sekarang memiliki field dokumen_stnk dan dokumen_bpkb.
2. Kedua dokumen hanya menerima file PDF pada form.
3. Halaman tambah/edit kendaraan menampilkan input Upload STNK (PDF) dan Upload BPKB (PDF).
4. Halaman detail kendaraan menampilkan preview PDF untuk STNK dan BPKB jika dokumen tersedia.

Setelah extract ZIP, jalankan:

```bash
cd sikaris
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver
```

Jika memakai Mac dan command python tidak tersedia, gunakan python3.
