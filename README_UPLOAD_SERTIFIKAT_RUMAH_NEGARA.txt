# Upload Sertifikat Rumah Negara PDF

Perubahan:
- Master Rumah Negara memiliki field baru `dokumen_sertifikat`.
- Form tambah/edit Rumah Negara menampilkan input Upload Sertifikat Rumah Negara (PDF).
- Validasi file hanya menerima PDF.
- Halaman detail Rumah Negara menampilkan preview PDF sertifikat dan tombol Buka PDF.

Setelah extract ZIP:
```bash
cd sikaris
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver
```

Jika di Mac command `python` tidak aktif, gunakan `python3`.
