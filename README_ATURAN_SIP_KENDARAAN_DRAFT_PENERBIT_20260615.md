# Perbaikan Aturan SIP Kendaraan

Perubahan ini menerapkan ketentuan:

1. Pengelola BMN hanya dapat membuat Draft/Konsep SIP Kendaraan.
2. Pengelola BMN hanya dapat mengajukan SIP Kendaraan kepada pejabat penerbit sesuai unit kerja.
3. Pengelola BMN tidak dapat memilih status Disetujui/Ditolak/Terbit dari form.
4. Pengelola BMN hanya dapat edit/hapus saat status Draft/Konsep atau Ditolak.
5. Tujuan pengajuan otomatis:
   - Unit Sekretariat Jenderal/Biro Umum -> Kepala Biro Umum.
   - Unit Eselon I selain Sekretariat Jenderal -> Sekretaris UKE I masing-masing.
   - Sentra -> Kepala Sentra.
   - Balai -> Kepala Balai.
6. Pejabat penerbit hanya dapat setujui/tolak SIP yang sudah diajukan sesuai kewenangannya.
7. Status SIP Kendaraan dinormalisasi menjadi: DRAFT, DIAJUKAN, DISETUJUI, DITOLAK, TERBIT, MENUNGGU_TTE, BERAKHIR, DIBATALKAN.

## File yang diubah

- `core/constants.py`
- `core/access.py`
- `core/notifications.py`
- `core/views.py`
- `kendaraan/forms.py`
- `kendaraan/models.py`
- `kendaraan/views.py`
- `kendaraan/sip_penerbit.py`
- `kendaraan/migrations/0006_normalisasi_status_sip_kendaraan.py`
- `templates/includes/generic_detail.html`
- `templates/kendaraan/sip_list.html`
- `templates/base.html`

## Setelah ekstrak ZIP

Jalankan:

```bash
python3 manage.py migrate
python3 manage.py setup_penerbit_sip_kendaraan
python3 manage.py runserver
```

Pastikan pada Master Unit Kerja sudah diisi pejabat penerbit SIP Kendaraan untuk:

- Biro Umum -> Kepala Biro Umum
- Sekretariat Ditjen/Itjen/Badan -> Sekretaris UKE I
- Sentra -> Kepala Sentra
- Balai -> Kepala Balai

Jika pejabat belum dikonfigurasi, saat klik Ajukan sistem akan menolak dan menampilkan pesan agar Master Unit Kerja dilengkapi.
