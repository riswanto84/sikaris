FITUR PERMOHONAN PENGHAPUSAN BMN - SIKARIS
================================================

Perubahan:
1. Menambahkan menu "Penghapusan BMN > Permohonan Penghapusan".
2. Unit kerja dapat mengajukan permohonan penghapusan BMN ke Biro Umum.
3. User Biro Umum/superuser dapat melihat dan memproses semua permohonan seluruh satker.
4. User unit kerja hanya dapat melihat/mengubah permohonan milik unit kerjanya.
5. Jenis aset yang didukung:
   - Kendaraan
   - Rumah Negara
   - Tanah Negara
   - BMN Lainnya
6. Data permohonan memuat:
   - Nomor dan tanggal permohonan
   - Unit kerja pemohon dan pegawai pemohon/PIC
   - Jenis aset, kode barang, NUP, nama barang, nilai perolehan
   - Kondisi/lokasi barang
   - Alasan penghapusan
   - Uraian alasan/kronologi
   - Dasar usulan
   - Dokumen usulan unit kerja
   - Dokumen pendukung
   - Foto kondisi aset
   - Catatan unit kerja
   - Catatan Biro Umum
   - Status proses
   - Nomor/tanggal persetujuan
   - Dokumen persetujuan
   - Nomor/tanggal SK penghapusan
   - Dokumen SK penghapusan
   - Berita acara penghapusan/pemusnahan/pemindahtanganan

Status permohonan:
- Draft
- Diajukan Unit Kerja
- Diverifikasi Biro Umum
- Perlu Perbaikan Usulan
- Ditolak
- Disetujui
- Proses Penghapusan
- Selesai/Dihapuskan

Catatan aturan akses:
- Biro Umum / superuser: dapat melihat dan memproses semua permohonan.
- User unit kerja: hanya dapat mengajukan/mengedit/menghapus permohonan unitnya sendiri selama belum diproses lebih lanjut oleh Biro Umum.
- Jika user unit kerja belum memiliki Unit Kerja/Satker pada Manajemen User, sistem akan menolak akses sampai unit kerja diisi.

Setelah extract ZIP jalankan:
python manage.py migrate
python manage.py seed_roles
python manage.py runserver

Dasar umum pengelolaan:
Fitur ini disusun mengikuti alur administratif penghapusan BMN: usulan unit kerja, penelitian/verifikasi, persetujuan/penolakan, penerbitan keputusan penghapusan, dan pelaporan/arsip dokumen.
