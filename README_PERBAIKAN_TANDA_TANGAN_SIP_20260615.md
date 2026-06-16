# Perbaikan Tanda Tangan SIP Kendaraan dan SIP Rumah Negara

Perbaikan ini menyesuaikan permintaan terbaru:

1. Kolom `pejabat_penandatangan` dihilangkan dari Form SIP Kendaraan.
2. Kolom `pejabat_penandatangan` dihilangkan dari Form SIP Rumah Negara.
3. Penandatangan SIP Kendaraan otomatis diambil dari Master Pegawai dengan jabatan yang mengandung teks `Kepala Biro Umum`.
4. Penandatangan SIP Rumah Negara otomatis diambil dari Master Pegawai dengan jabatan yang mengandung teks `Sekretaris Jenderal`.
5. Blok tanda tangan PDF SIP dirapikan agar nama dan NIP kedua pihak sejajar dalam baris yang sama.
6. Semua area tanda tangan diberi keterangan TTE BSrE / Menunggu Persetujuan TTE BSrE.

Catatan penting:
- Pastikan data Master Pegawai untuk Kepala Biro Umum sudah ada dan aktif.
- Pastikan data Master Pegawai untuk Sekretaris Jenderal sudah ada dan aktif.
- Jika data master belum ditemukan, sistem memakai fallback yang sudah tersedia agar PDF tetap bisa dibuat.

File yang diperbaiki:
- `kendaraan/forms.py`
- `kendaraan/models.py`
- `rumah_dinas/forms.py`
- `rumah_dinas/models.py`
- `core/pdf_sip.py`
