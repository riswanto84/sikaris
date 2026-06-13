# SIKARIS - Sistem Informasi Kendaraan dan Rumah Dinas

Versi ini sudah diperbaiki dengan:

- Menu **Master Unit Kerja**.
- Pembatasan akses berdasarkan role:
  - **Admin System**: akses penuh, termasuk Django Admin.
  - **Pengelola BMN**: master data, SIP kendaraan, SIP rumah dinas, perbaikan rumah, laporan.
  - **Pemeliharaan Kendaraan**: daftar kendaraan, lihat SIP kendaraan, service kendaraan, update kondisi kendaraan, laporan terbatas.
- Tampilan modern: sidebar, topbar, card dashboard, badge kondisi, animasi counter, filter cepat tabel, dashboard AJAX.
- Model dan migration awal sudah disertakan.

## Cara menjalankan

```bash
cd sikaris
python -m venv venv
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles
python manage.py runserver
```

Buka: http://127.0.0.1:8000/

## User Demo

- `adminsystem` / `Password123!`
- `bmn` / `Password123!`
- `pemeliharaan` / `Password123!`

## Catatan

Gunakan folder baru dan database baru ketika mencoba versi ini agar tidak bentrok dengan migration/database lama.


## Format Rupiah

Aplikasi sudah menyediakan template filter:

```django
{% load rupiah %}
{{ nilai|rupiah }}
```

Contoh hasil:
- `499900000` menjadi `Rp 499.900.000`
- `499900000.50` menjadi `Rp 499.900.000,50`
