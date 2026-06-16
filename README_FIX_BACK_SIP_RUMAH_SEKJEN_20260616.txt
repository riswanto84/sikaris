Perbaikan tombol Kembali Detail SIP Rumah Negara untuk role Sekjen:

1. Jika Detail SIP Rumah Negara dibuka oleh role Sekretaris Jenderal/Admin System,
   tombol Kembali sekarang diarahkan ke menu Persetujuan Sekjen - SIP Rumah Negara.
2. Perbaikan tetap mempertahankan parameter next URL yang aman jika detail dibuka dari hasil pencarian.
3. Kondisi ini memperbaiki error saat Detail SIP Rumah Negara dibuka dari notifikasi atau setelah aksi setujui/tolak/upload TTE,
   karena sebelumnya fallback dapat mengarah ke daftar SIP umum Pengelola BMN.
4. Tidak membutuhkan migrasi database.
