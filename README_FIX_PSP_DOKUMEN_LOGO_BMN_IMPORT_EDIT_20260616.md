# Perbaikan PSP BMN - Dokumen, Logo, dan Akses BMN

Perubahan:

1. Tombol generate/export Lampiran Daftar Barang PDF pada detail PSP dihapus.
   - Detail barang tetap dapat diimport Excel dan ditampilkan pada detail PSP.
   - Data barang tetap tersimpan sebagai data pendukung, tetapi tidak digenerate sebagai PDF lampiran dari SIM Pengelolaan BMN.

2. Kop Nota Dinas/Surat Keterangan/Surat Pernyataan PSP diperbaiki.
   - Logo Kemensos tampil di kiri atas dokumen.
   - Format mengikuti contoh dokumen Biro Umum.

3. Nama dan NIP pejabat pada dokumen PSP tidak lagi kosong.
   - Jika field pejabat TTE pada permohonan belum diisi, sistem mengambil fallback dari Master Pegawai jabatan Kepala Biro Umum.
   - Jika belum ditemukan, fallback terakhir memakai Salahuddin / 197004281998031004.

4. Role BMN diizinkan Edit dan Import Barang pada menu Permohonan PSP BMN sesuai scope kewenangannya.
   - Role Sekjen tetap tidak dapat edit/import/hapus melalui form umum.

5. File logo PNG ditambahkan di static/img/logo-kemensos.png agar ReportLab dapat memasukkan logo ke PDF.
