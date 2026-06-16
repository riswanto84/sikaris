Perbaikan Detail SIP Kendaraan untuk Role Pengelola BMN
======================================================

Perubahan:
1. Role Pengelola BMN tidak lagi melihat tombol Edit/Hapus pada halaman Detail SIP Kendaraan.
2. Role Pengelola BMN tidak lagi bisa generate Konsep PDF dari halaman Detail SIP Kendaraan.
3. Role Pengelola BMN tidak lagi bisa upload PDF SIP Kendaraan yang sudah TTE BSrE.
4. Role Pengelola BMN hanya dapat mengajukan SIP berstatus DRAFT/DITOLAK kepada pejabat penerbit.
5. Endpoint generate PDF, setujui/tolak, dan upload BSrE juga diberi guard agar Pengelola BMN tidak bisa mengakses langsung lewat URL.

Alur final:
- Pengelola BMN: membuat draft/konsep, melihat detail, dan mengajukan.
- Pejabat penerbit: review, generate konsep/final PDF, setujui/tolak, upload PDF TTE BSrE.
