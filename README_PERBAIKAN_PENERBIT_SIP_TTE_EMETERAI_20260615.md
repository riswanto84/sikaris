# Perbaikan SIKARIS - Penerbit SIP Kendaraan, TTE, dan e-Meterai

## Aturan yang diterapkan

1. Penerbit SIP Kendaraan tidak lagi selalu Kepala Biro Umum.
2. Penerbit SIP Kendaraan mengikuti konfigurasi pada Master Unit Kerja:
   - Biro Umum: Kepala Biro Umum
   - Unit Direktorat Jenderal/Itjen/Badan: Sekretaris unit Eselon I masing-masing
   - Sentra: Kepala Sentra
   - Balai: Kepala Balai
   - Pusat/unit lain: Kepala/pejabat yang dikonfigurasi admin
3. e-Meterai hanya tersedia pada fitur PSP BMN. Tidak ditambahkan ke SIP Kendaraan/Rumah Negara.
4. TTE tersedia untuk dokumen yang memerlukan tanda tangan elektronik. Pada SIP memakai file signed/TTE, pada PSP memakai field TTE BSrE yang sudah ada.

## File penting yang berubah

- `master/models.py`: menambahkan konfigurasi penerbit SIP Kendaraan pada `UnitKerja`.
- `kendaraan/models.py`: menambahkan snapshot pejabat penerbit SIP Kendaraan dan status TTE.
- `rumah_dinas/models.py`: menambahkan status TTE untuk SIP Rumah Negara.
- `penghapusan/models.py`: menambahkan status/file TTE untuk dokumen penghapusan BMN yang membutuhkan TTE.
- `kendaraan/sip_penerbit.py`: logika penentuan pejabat penerbit berdasarkan unit kerja.
- `kendaraan/views.py`: approval SIP Kendaraan diarahkan ke pejabat penerbit sesuai unit.
- `core/pdf_sip.py`: tanda tangan PDF SIP Kendaraan mengambil snapshot pejabat penerbit.
- `core/roles.py`: menambah role `Pejabat Penerbit SIP`, `Sekretaris Ditjen`, `Sekretaris Eselon I`, `Kepala Sentra`, dan `Kepala Balai`.
- `master/management/commands/setup_penerbit_sip_kendaraan.py`: command bantu konfigurasi awal.

## Cara menjalankan setelah ekstrak ZIP

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py setup_penerbit_sip_kendaraan
python manage.py runserver
```

Setelah itu buka menu Master Unit Kerja, lalu cek/isikan:

- Jenis Unit
- Pejabat Penerbit SIP Kendaraan
- Nama Jabatan Penerbit SIP Kendaraan

User pejabat penerbit perlu diberi role yang sesuai dan unit kerja pada Manajemen User.
