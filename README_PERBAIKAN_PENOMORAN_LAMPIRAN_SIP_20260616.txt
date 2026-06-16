PERBAIKAN PENOMORAN OTOMATIS DAN LAMPIRAN KONSEP SIP
======================================================

Perubahan:
1. Penomoran SIP Rumah Negara otomatis memakai format:
   nomor/1.5/PL.03/SIKARIS/bulan/tahun
   Contoh: 1/1.5/PL.03/SIKARIS/01/2026

2. Penomoran SIP Kendaraan otomatis memakai format:
   nomor/1/PL.02/SIKARIS/bulan/tahun
   Contoh: 2/1/PL.02/SIKARIS/01/2025

3. Nomor urut otomatis meneruskan nomor sebelumnya:
   - sistem membaca nomor urut terbesar yang sudah ada pada tahun berjalan,
   - kemudian memperbarui sequence NomorSuratSequence agar tidak mundur.

4. Generate konsep PDF SIP Rumah Negara sekarang berisi:
   - halaman SIP Rumah Negara,
   - foto pemegang SIP jika tersedia di Master Pegawai,
   - lampiran Surat Pernyataan,
   - area e-Meterai elektronik,
   - area TTE BSrE calon pengguna rumah,
   - lampiran foto rumah negara dari Master Rumah Negara.

Catatan penting:
- Area e-Meterai dan TTE pada konsep PDF adalah area/placeholder dokumen untuk proses TTE/e-Meterai resmi.
- Pembubuhan e-Meterai dan TTE sebenarnya tetap dilakukan melalui layanan resmi yang digunakan instansi.
- Jika foto pemegang SIP atau foto rumah belum tersedia, PDF akan menampilkan kotak placeholder.
