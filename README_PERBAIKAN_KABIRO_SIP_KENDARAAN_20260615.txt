PERBAIKAN 15 Juni 2026 - Persetujuan SIP Kendaraan oleh Kepala Biro Umum

Perubahan utama:
1. Menambahkan role bawaan baru: Kepala Biro Umum.
2. SIP Kendaraan tidak lagi diajukan/disetujui oleh Sekretaris Jenderal.
3. SIP Kendaraan sekarang diajukan/disetujui/ditolak oleh Kepala Biro Umum.
4. SIP Rumah Negara/Rumah Dinas tetap diajukan/disetujui/ditolak oleh Sekretaris Jenderal.
5. Menu persetujuan dipisah:
   - Persetujuan Kepala Biro Umum: SIP Kendaraan.
   - Persetujuan Sekjen: SIP Rumah Negara.
6. Notifikasi lonceng Kepala Biro Umum aktif untuk SIP Kendaraan berstatus DIAJUKAN_KABIRO.
7. Notifikasi lonceng Sekjen tetap khusus SIP Rumah Negara berstatus DIAJUKAN_SEKJEN.
8. Tombol Hapus disembunyikan untuk role Sekjen dan Kepala Biro Umum.
9. PDF SIP Kendaraan memakai blok tanda tangan Kepala Biro Umum.
10. PDF SIP Rumah Negara tetap memakai blok tanda tangan Sekretaris Jenderal.

Setelah update, jalankan:
python3 manage.py migrate

Jika memakai command demo:
python3 manage.py seed_roles

User demo baru:
- kabiroumum / Password123! / role Kepala Biro Umum
- sekjen / Password123! / role Sekretaris Jenderal
