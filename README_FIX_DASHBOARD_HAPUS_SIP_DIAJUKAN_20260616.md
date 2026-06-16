# Perbaikan Dashboard - Hapus SIP Diajukan

Perubahan:

1. Kartu **SIP Kendaraan Diajukan** dihapus dari dashboard.
2. Kartu **SIP Rumah Negara Diajukan** dihapus dari dashboard.
3. Counter `sip_kendaraan_diajukan` dan `sip_rumah_diajukan` dihapus dari context dashboard karena tidak lagi digunakan di tampilan.
4. Kartu Draft/Konsep, Terbit, dan Akan Berakhir tetap dipertahankan agar lebih sesuai dengan alur data yang saat ini banyak berstatus DRAFT.

Tidak ada perubahan database dan tidak perlu migrasi.
