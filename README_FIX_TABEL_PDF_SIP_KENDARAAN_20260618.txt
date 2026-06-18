PERBAIKAN FORMAT TABEL PDF SIP KENDARAAN - 18 Juni 2026

Perubahan:
1. Format tabel spesifikasi kendaraan pada PDF SIP Kendaraan disesuaikan dengan contoh:
   - NO.
   - KODE BARANG
   - NUP
   - JENIS KENDARAAN
   - MERK
   - NO. RANGKA
   - NO. MESIN
   - NO. POLISI
   - TAHUN PEROLEHAN
2. Tabel dibuat rata kiri (hAlign='LEFT') agar sejajar/justify dengan paragraf kalimat SIP.
3. Lebar kolom disesuaikan agar tabel tidak terlalu melebar dan tidak tampak bergeser ke tengah.
4. Baris Kunci Kendaraan serta STNK dan Surat Pajak Kendaraan tetap mengikuti format contoh dengan span kolom.
5. Tahun perolehan mengambil dari tanggal_perolehan bila tersedia, fallback ke tahun_perolehan.

File yang diubah:
- core/pdf_sip.py

Tidak ada perubahan model/database, sehingga tidak perlu makemigrations.
Cukup restart server Django setelah file diperbarui.
