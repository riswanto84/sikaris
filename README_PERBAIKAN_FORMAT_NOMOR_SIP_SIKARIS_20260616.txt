PERBAIKAN FORMAT NOMOR SIP OTOMATIS - SIKARIS

1. Format nomor SIP Rumah Negara diubah menjadi:
   nomor/1.5/PL.03/SIKARIS/bulan/tahun
   Contoh: 1/1.5/PL.03/SIKARIS/01/2026

2. Format nomor SIP Kendaraan diubah menjadi:
   nomor/1/PL.02/SIKARIS/bulan/tahun
   Contoh: 2/1/PL.02/SIKARIS/01/2025

3. Nomor urut tetap otomatis meneruskan nomor terbesar sebelumnya pada tahun berjalan.

4. Perubahan dilakukan pada fungsi core.models.next_nomor_surat dan help_text model SIP.

5. Tidak ada perubahan struktur database, sehingga tidak wajib migrasi.
