PERBAIKAN 15 Juni 2026 - Role Sekjen, Notifikasi SIP, dan PDF SIP Kendaraan

Perubahan yang diterapkan:
1. Role Sekretaris Jenderal diperbolehkan membuka fitur edit SIP Kendaraan dan SIP Rumah Negara.
2. Scope data SIP untuk Sekretaris Jenderal dibuka lintas satker/unit kerja agar proses review/persetujuan tidak terkena 403 Forbidden.
3. Dropdown form SIP saat diedit Sekretaris Jenderal tidak dibatasi unit kerja, sehingga data lama tetap tampil dan bisa diedit.
4. Tombol Hapus pada halaman detail disembunyikan untuk role Sekretaris Jenderal.
5. Permission delete tetap tidak diberikan kepada Sekretaris Jenderal karena view delete masih memakai role pengelola/admin/Biro Umum.
6. Notifikasi lonceng untuk Sekretaris Jenderal diaktifkan untuk SIP Kendaraan dan SIP Rumah Negara dengan status DIAJUKAN_SEKJEN.
7. Template PDF SIP Kendaraan dirapikan: tabel memakai Paragraph agar teks membungkus, kolom disesuaikan, baris Kunci Kendaraan dan STNK memakai colspan/span agar tidak tumpang tindih.

File yang diubah:
- core/roles.py
- core/access.py
- core/notifications.py
- core/pdf_sip.py
- kendaraan/views.py
- rumah_dinas/views.py
- templates/includes/generic_detail.html

Catatan:
- Untuk melihat hasil PDF yang sudah rapi, buka detail SIP kendaraan lalu klik Generate Konsep PDF ulang.
- Jika sebelumnya PDF lama sudah tersimpan, file lama tidak otomatis berubah sampai generate ulang dilakukan.
