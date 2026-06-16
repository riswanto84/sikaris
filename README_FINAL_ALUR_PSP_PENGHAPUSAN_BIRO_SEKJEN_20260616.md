# Perbaikan Alur PSP BMN dan Penghapusan BMN

Tanggal: 16 Juni 2026

## PSP BMN

Alur dipisahkan menjadi tiga fitur/menu:

1. **Permohonan PSP BMN**
   - Digunakan oleh unit kerja/satker untuk membuat dan mengajukan usulan PSP.
   - Unit kerja hanya mengelola usulan awal dan perbaikan.

2. **Verifikasi Usulan PSP BMN - Biro Umum**
   - Digunakan oleh role Biro Umum.
   - Biro Umum dapat membaca semua usulan PSP seluruh unit kerja, memverifikasi, mengembalikan untuk perbaikan, atau meneruskan ke Sekjen.

3. **Penetapan PSP BMN - Sekjen**
   - Digunakan oleh role Sekretaris Jenderal.
   - Sekjen dapat membaca semua PSP lintas unit kerja dan menetapkan/menolak PSP.
   - SK final/TTE BSrE dapat diunggah dari halaman detail penetapan.

## Penghapusan BMN

Alur dipisahkan menjadi tiga fitur/menu:

1. **Permohonan Penghapusan BMN**
   - Digunakan oleh unit kerja/satker untuk membuat usulan penghapusan.

2. **Verifikasi Usulan Penghapusan BMN - Biro Umum**
   - Digunakan oleh role Biro Umum.
   - Biro Umum dapat membaca semua usulan penghapusan, memverifikasi, mengembalikan untuk perbaikan, atau meneruskan ke Sekjen.

3. **Penetapan SK Penghapusan BMN - Sekjen**
   - Digunakan oleh role Sekretaris Jenderal.
   - Sekjen menetapkan SK Penghapusan BMN berdasarkan usulan yang diteruskan Biro Umum.
   - Dokumen SK final/TTE BSrE dapat diunggah dari halaman detail penetapan.

## Catatan Teknis

- Perubahan ini tidak menambah tabel baru.
- Tidak perlu migrasi database.
- Menambahkan route baru:
  - `psp:verifikasi`
  - `psp:persetujuan_sekjen`
  - `psp:proses`
  - `penghapusan:verifikasi`
  - `penghapusan:persetujuan_sekjen`
  - `penghapusan:proses`
