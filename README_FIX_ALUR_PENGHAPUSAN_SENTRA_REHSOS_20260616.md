# Perbaikan Alur Nota Dinas Penghapusan BMN Sentra Rehsos

Perbaikan ini menyesuaikan rule bisnis penghapusan BMN:

1. Jika usulan penghapusan berasal dari **Sentra di bawah Direktorat Jenderal Rehabilitasi Sosial**, maka alurnya berjenjang:
   - Tahap 1: Kepala Sentra -> Direktur Jenderal Rehabilitasi Sosial.
   - Tahap 2: Direktur Jenderal Rehabilitasi Sosial -> Sekretaris Jenderal.

2. Jika usulan penghapusan berasal dari **Balai**, maka nota dinas langsung:
   - Kepala Balai -> Sekretaris Jenderal.

3. Jika usulan penghapusan berasal dari **Unit Pusat/Eselon I**, maka nota dinas:
   - Sekretaris Unit Eselon I -> Sekretaris Jenderal.

Perubahan teknis:
- Helper `get_alur_nota_penghapusan()` sekarang mengembalikan tahapan lengkap untuk Sentra Rehsos.
- Detail Permohonan Penghapusan BMN menampilkan tahapan nota dinas secara berurutan.
- Pesan sukses saat Biro Umum meneruskan usulan menampilkan alur berjenjang untuk Sentra Rehsos.

Tidak ada perubahan struktur database.
