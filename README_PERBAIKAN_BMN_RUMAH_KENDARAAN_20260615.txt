PERBAIKAN 15 JUNI 2026

1. Form Master Kendaraan
   - Field Pengguna dihilangkan dari form tambah/edit kendaraan.
   - Pengguna kendaraan dicatat melalui SIP Kendaraan, bukan di master kendaraan.
   - Daftar/detail kendaraan tidak lagi menampilkan field Pengguna.
   - Import kendaraan tidak lagi mengisi pengguna_nip ke master kendaraan.

2. Role Pengelola BMN
   - Role Pengelola BMN dapat CRUD data Rumah Negara.
   - Tambah Rumah Negara tidak lagi dibatasi hanya Biro Umum.
   - Scope data Pengelola BMN dibuat dapat melihat/mengelola data master sesuai kebutuhan pengelolaan BMN.

3. Menu Unit Kerja
   - Link menu Unit Kerja disembunyikan untuk role Pengelola BMN.
   - Link Unit Kerja hanya tampil untuk Admin System atau Biro Umum.

Catatan:
- Database tidak diubah/dihapus agar data lama tetap aman.
- Field pengguna di model kendaraan tetap dipertahankan untuk kompatibilitas data lama, namun tidak dipakai lagi pada form master kendaraan.
