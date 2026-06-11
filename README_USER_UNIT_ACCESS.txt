# Update Manajemen User: Field Unit Kerja/Satker

Versi ini menambahkan field **Unit Kerja / Satker** pada menu:

- Manajemen User > Tambah User
- Manajemen User > Edit User
- Manajemen User > Daftar User

## Konsep akses

1. **Biro Umum / superuser**
   - Bisa melihat dan CRUD seluruh data semua unit kerja/satker.

2. **User unit kerja lainnya**
   - Hanya bisa melihat dan CRUD data kendaraan, SIP kendaraan, service kendaraan, riwayat kondisi, rumah dinas, dan SIP rumah dinas sesuai **Unit Kerja/Satker** yang dipilih pada Manajemen User.

3. **Prioritas pembatasan akses**
   - Sistem memprioritaskan field `Unit Kerja/Satker` pada profil user.
   - Jika field tersebut kosong, sistem masih memakai mekanisme lama yaitu mencocokkan user dengan data pegawai berdasarkan NIP/email.

## Langkah setelah update kode

Jalankan:

```bash
python manage.py migrate
python manage.py seed_roles
python manage.py runserver
```

## Catatan penting

Untuk membuat user unit kerja, Admin System wajib memilih Unit Kerja/Satker pada form Tambah/Edit User. Jika kosong, user non-Biro Umum dapat terkena error permission karena sistem tidak tahu unit mana yang boleh diakses.
