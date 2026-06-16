# Perbaikan Alur Penghapusan BMN disamakan dengan PSP BMN

Perubahan 2026-06-16:

1. Penghapusan BMN dipisahkan mengikuti pola PSP:
   - Permohonan Penghapusan BMN oleh Unit Kerja/Pengelola BMN.
   - Verifikasi Usulan Penghapusan oleh Biro Umum.
   - Persetujuan Dirjen Rehsos khusus usulan dari Sentra di bawah Ditjen Rehsos.
   - Penetapan SK Penghapusan oleh Sekretaris Jenderal.

2. Status alur baru:
   - DRAFT
   - DIAJUKAN_UNIT_KERJA
   - MENUNGGU_VERIFIKASI_BIRO_UMUM
   - DIVERIFIKASI_BIRO_UMUM
   - PERLU_PERBAIKAN
   - DIAJUKAN_KE_DIRJEN_REHSOS
   - DISETUJUI_DIRJEN_REHSOS
   - DITOLAK_DIRJEN_REHSOS
   - DIAJUKAN_KE_SEKJEN
   - DITOLAK_SEKJEN
   - SK_PENGHAPUSAN_TERBIT
   - SELESAI

3. Rule berjenjang:
   - Sentra di bawah Ditjen Rehsos: Kepala Sentra → Dirjen Rehsos → Sekretaris Jenderal.
   - Balai: Kepala Balai → Sekretaris Jenderal.
   - Unit pusat: Sekretaris Unit Eselon I → Sekretaris Jenderal.

4. Sebelum diteruskan dari Biro Umum, Dokumen Penghapusan SIKARIS Final/Gabungan PDF wajib diupload.

5. Role Sekjen hanya menetapkan/menolak dan upload SK final, tidak edit umum.

Catatan: Role baru untuk menu persetujuan Sentra Rehsos adalah "Direktur Jenderal Rehabilitasi Sosial".
