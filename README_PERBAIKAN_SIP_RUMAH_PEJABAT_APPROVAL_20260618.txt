PERBAIKAN SIP RUMAH NEGARA - PEJABAT PENANDATANGAN DAN REVIEW PERSETUJUAN
Tanggal: 18 Juni 2026

Perubahan:
1. Form SIP Rumah Negara:
   - Nama Pejabat Penandatangan tetap dipilih dari Master Pegawai.
   - Jabatan Pejabat Penandatangan ditampilkan otomatis dari Master Pegawai.
   - Field Jabatan Pejabat Penandatangan dibuat non-editable/readonly.
   - Saat Nama Pejabat Penandatangan dipilih, field Jabatan otomatis berubah di form.
   - Saat data disimpan, snapshot nama, NIP, dan jabatan pejabat penandatangan ikut disimpan untuk kebutuhan PDF.

2. Detail/Review SIP Rumah Negara:
   - Ditambahkan panel Review Persetujuan SIP Rumah Negara.
   - Tombol Setujui SIP dilengkapi kolom Keterangan Persetujuan.
   - Tombol Tolak SIP dilengkapi Alasan Penolakan wajib dan Keterangan Tambahan.
   - Keterangan persetujuan disimpan pada field catatan.
   - Alasan/keterangan penolakan disimpan pada field catatan_penolakan.

3. Database:
   - Tidak ada field baru.
   - Tidak perlu makemigrations/migrate khusus untuk perbaikan ini.

Setelah extract ZIP:
- Restart server Django.
- Jika sebelumnya belum menjalankan migration dari paket sebelumnya, tetap jalankan migration paket sebelumnya terlebih dahulu.
