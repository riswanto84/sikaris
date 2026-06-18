PERBAIKAN FORM SIP RUMAH NEGARA - PEJABAT PENANDATANGAN DAN UPLOAD TTE
Tanggal: 18 Juni 2026

Perubahan:
1. Form SIP Rumah Negara untuk role Pengelola BMN ditambahkan field:
   - Nama Pejabat Penandatangan
   - Upload SIP Rumah Negara yang sudah TTE

2. Nama Pejabat Penandatangan berupa dropdown dari Master Pegawai.
   Saat disimpan, sistem menyimpan snapshot:
   - nama pejabat penandatangan
   - NIP pejabat penandatangan
   - jabatan pejabat penandatangan

3. PDF SIP Rumah Negara mengambil pejabat penandatangan dari field yang dipilih pada form.

4. Jika file SIP yang sudah TTE diupload melalui form:
   - file tersimpan pada file_signed_pdf
   - file juga disalin sebagai dokumen_sip untuk kompatibilitas preview lama
   - status_tte otomatis menjadi SUDAH_TTE
   - tanggal_tte otomatis terisi

5. Preview PDF di bawah halaman form tetap menampilkan konsep/final PDF.

File yang diubah:
- rumah_dinas/models.py
- rumah_dinas/forms.py
- core/pdf_sip.py
- templates/rumah_dinas/form.html

Migration baru:
- rumah_dinas/migrations/0011_pejabat_penandatangan_tte_form_sip_rumah.py

Setelah ekstrak ZIP, jalankan:
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
