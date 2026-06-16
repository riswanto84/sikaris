# Perbaikan Fitur Import Unit Kerja

Perubahan:

1. Menu Master Unit Kerja ditambahkan tombol **Import Excel/CSV**.
2. Ditambahkan tombol **Download Template Import** untuk Unit Kerja.
3. File import mendukung format `.xlsx`, `.xlsm`, dan `.csv`.
4. Kolom yang didukung:
   - `nama_unit` wajib; menjadi kunci tambah/update.
   - `jenis_unit` opsional; contoh: `BIRO_UMUM`, `DITJEN`, `ITJEN`, `BADAN`, `PUSAT`, `SENTRA`, `BALAI`, `LAINNYA`.
   - `nama_jabatan_penerbit_sip_kendaraan` opsional.
   - `pejabat_penerbit_nip` opsional; diisi NIP pegawai yang sudah ada pada Master Pegawai.
   - `keterangan` opsional.
5. Akses import Unit Kerja dibatasi untuk Admin System/Biro Umum sesuai aturan menu Unit Kerja.

Tidak ada perubahan struktur database, sehingga tidak perlu migrasi.
