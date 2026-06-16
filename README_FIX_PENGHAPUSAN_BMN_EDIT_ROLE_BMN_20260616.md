# Perbaikan Permohonan Penghapusan BMN - Edit Role Pengelola BMN

Perubahan:

1. Role Pengelola BMN yang memiliki scope data sesuai unit/eselon I/sentra/balai kini dapat membuka tombol **Edit** pada menu **Permohonan Penghapusan BMN** tanpa terkena error **403 Forbidden**.
2. Keamanan scope tetap menggunakan `get_scoped_queryset()`, sehingga user hanya bisa mengedit data yang memang masuk kewenangannya.
3. Status permohonan tidak lagi dipaksa kembali menjadi `DIAJUKAN` setiap kali diedit. Status lama dipertahankan agar alur Verifikasi Biro Umum dan Penetapan Sekjen tidak kacau.
4. Khusus status `DRAFT` dan `PERLU_PERBAIKAN`, setelah diperbaiki oleh Pengelola BMN status dinaikkan kembali menjadi `DIAJUKAN`.
5. Import Barang Penghapusan juga diperbolehkan untuk Role Pengelola BMN selama permohonan belum selesai/SK terbit.
6. Role Sekjen tetap tidak dapat mengedit/import/hapus dari menu permohonan umum.

Tidak ada perubahan struktur database, sehingga tidak perlu migrasi.
