ARSIP DOKUMEN SIP KENDARAAN DAN RUMAH NEGARA
================================================

Dokumen dari file Arsip.zip sudah digabungkan ke folder:

media/arsip_sip/kendaraan/
media/arsip_sip/rumah_negara/

Jumlah dokumen PDF yang digabungkan:
- Arsip SIP Kendaraan: 201 file
- Arsip SIP Rumah Negara/Rumah Dinas: 22 file
- Total: 223 file

Cara menghubungkan dokumen arsip ke data SIP yang sudah ada di database:

1. Jalankan migrasi terlebih dahulu:
   python manage.py migrate

2. Cek simulasi pencocokan dokumen tanpa mengubah database:
   python manage.py sync_arsip_sip --dry-run

3. Jika hasilnya sudah sesuai, jalankan sinkronisasi:
   python manage.py sync_arsip_sip

4. Jika ingin menimpa dokumen SIP yang sebelumnya sudah ada:
   python manage.py sync_arsip_sip --replace

Cara kerja pencocokan:
- Dokumen SIP Kendaraan dicocokkan berdasarkan nomor polisi pada nama file, misalnya B 1307 PQH.
- Dokumen SIP Rumah Negara dicocokkan berdasarkan nama pegawai/penghuni pada nama file, misalnya nama dalam tanda kurung.
- Jika data SIP belum ada di database, dokumen tetap tersimpan di folder media/arsip_sip dan dapat diupload manual dari form SIP.

Laporan sinkronisasi otomatis dibuat di:
media/arsip_sip/laporan_sync_arsip_sip.csv

Catatan:
- Folder media/arsip_sip sengaja dimasukkan ke ZIP agar dokumen arsip ikut terbawa ke aplikasi.
- File PDF/JPG/JPEG/PNG dari Arsip.zip disertakan. File __MACOSX dan resource fork dari arsip Mac tidak disertakan.
- Command sync_arsip_sip otomatis menghubungkan file PDF SIP ke field dokumen_sip. File STNK berupa gambar tetap tersimpan sebagai arsip pendukung di media/arsip_sip/kendaraan/.
