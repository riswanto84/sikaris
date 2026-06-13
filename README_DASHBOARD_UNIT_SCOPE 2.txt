# Update Dashboard Berdasarkan Unit Kerja User

Perubahan ini membuat seluruh ringkasan Dashboard mengikuti hak akses Unit Kerja/Satker user.

## Aturan

- Superuser dan user dengan role/grup `Biro Umum` melihat data semua satker/unit kerja.
- User unit kerja lain hanya melihat ringkasan data sesuai field `Unit Kerja/Satker` pada menu Manajemen User.
- Jika field Unit Kerja/Satker pada user belum diisi, sistem memakai fallback lama berdasarkan NIP/email pegawai.

## Data Dashboard yang sudah difilter

- Total kendaraan
- Kondisi kendaraan baik/rusak ringan/rusak berat
- Total rumah dinas
- Kondisi rumah dinas baik/rusak ringan/rusak berat
- Total pegawai
- Total unit kerja
- SIP kendaraan aktif dan akan berakhir
- SIP rumah dinas aktif dan akan berakhir
- Service kendaraan bulan ini
- Total biaya service bulan ini
- Perbaikan rumah dinas
- Aktivitas service terakhir
- Kendaraan perlu tindakan

## File yang diubah

- `core/views.py`
- `core/access.py`
- `templates/core/dashboard.html`

## Cara menjalankan setelah extract

```bash
cd sikaris
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver
```
