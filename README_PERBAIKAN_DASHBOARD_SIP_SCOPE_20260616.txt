PERBAIKAN DASHBOARD PERMOHONAN SIP SESUAI KEWENANGAN ROLE

Perubahan:
1. Dashboard menampilkan ringkasan permohonan SIP Kendaraan sesuai scope user:
   - Total Permohonan SIP Kendaraan
   - SIP Kendaraan Draft
   - SIP Kendaraan Diajukan
   - SIP Kendaraan Terbit
   - SIP Kendaraan Akan Berakhir
2. Dashboard menampilkan ringkasan permohonan SIP Rumah Negara sesuai scope user:
   - Total Permohonan SIP Rumah Negara
   - SIP Rumah Negara Diajukan
   - SIP Rumah Negara Terbit
3. Query dashboard tetap memakai scope_queryset_by_user sehingga:
   - Admin melihat semua data.
   - Pengelola BMN Biro Umum melihat data Sekretariat Jenderal.
   - Pengelola BMN Sekretariat Eselon I melihat data Eselon I masing-masing.
   - Pengelola BMN Sentra/Balai melihat data sentra/balainya sendiri.
   - Pejabat penerbit SIP Kendaraan melihat data SIP Kendaraan sesuai kewenangannya.
4. Link Lihat Detail SIP Kendaraan di dashboard diarahkan sesuai hak akses:
   - Pengelola BMN/Admin ke Daftar SIP Kendaraan.
   - Pejabat penerbit ke Persetujuan SIP Kendaraan.

Tidak perlu migrasi database.
