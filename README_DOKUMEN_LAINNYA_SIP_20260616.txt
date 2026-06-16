PERBAIKAN DOKUMEN LAINNYA / LAMPIRAN PENDUKUNG SIP

1. SIP Kendaraan
   - Ditambahkan field Dokumen Lainnya / Lampiran Pendukung (Opsional).
   - Field ini tampil pada Form SIP Kendaraan.
   - Dokumen SIP utama tetap digenerate sistem, bukan diupload manual dari form.
   - Lampiran yang didukung: PDF, JPG, JPEG, PNG, WEBP, DOC, DOCX, XLS, XLSX.

2. SIP Rumah Negara
   - Ditambahkan field Dokumen Lainnya / Lampiran Pendukung (Opsional).
   - Field ini tampil pada Form SIP Rumah Negara.
   - Dokumen SIP utama tetap digenerate sistem.
   - Lampiran yang didukung: PDF, JPG, JPEG, PNG, WEBP, DOC, DOCX, XLS, XLSX.

3. Detail SIP
   - File lampiran pendukung otomatis tampil pada halaman Detail SIP sebagai link Lihat file.

4. Setelah update ZIP jalankan:
   python3 manage.py migrate
   python3 manage.py runserver
