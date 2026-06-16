# Perbaikan PSP BMN - Hapus Kolom Jumlah/Nilai

Perubahan:

1. Kolom **Jumlah/Nilai** pada daftar Permohonan PSP BMN dihapus.
2. Tampilan nilai **1 unit / Rp ...** pada daftar PSP dihapus agar tabel lebih ringkas.
3. Data jumlah barang dan nilai tetap tersimpan di database dan tetap bisa dipakai untuk validasi serta detail, tetapi tidak ditampilkan pada tabel daftar.
4. Colspan empty-state disesuaikan dari 10 menjadi 9 kolom.

File yang diubah:
- `templates/psp/list.html`

Tidak perlu migrasi database.
