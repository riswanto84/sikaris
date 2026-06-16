PERBAIKAN PDF SIP RUMAH NEGARA / RUMAH DINAS - 15 JUNI 2026

Perubahan:
1. Template generate PDF SIP Rumah Negara pada core/pdf_sip.py dirapikan.
2. Seluruh isi tabel/kolom di PDF Rumah Negara memakai Paragraph ReportLab agar teks panjang otomatis turun baris.
3. Tabel keluarga diberi lebar kolom tetap, font kecil, padding rapi, dan word wrap.
4. Bagian data pegawai dan keterangan rumah dirapikan agar alamat, jabatan, unit organisasi, jenis rumah, dan masa berlaku SIP tidak saling tumpang tindih.
5. Karakter khusus seperti &, <, > dibuat aman untuk PDF agar tidak merusak layout.

Catatan:
- PDF lama yang sudah tersimpan tidak otomatis berubah.
- Buka Detail SIP Rumah Negara, lalu klik Generate Konsep PDF ulang agar file PDF memakai layout baru.
