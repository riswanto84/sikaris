Perbaikan SIP Kendaraan - 18 Juni 2026

1. Form SIP Kendaraan ditambahkan field:
   - Upload SIP Kendaraan yang sudah TTE
   Field ini menerima file PDF dan bersifat opsional.

2. Jika file SIP yang sudah TTE diupload melalui Form SIP Kendaraan:
   - file disimpan ke file_signed_pdf,
   - disalin sebagai dokumen_sip untuk preview/detail lama,
   - status_tte menjadi SUDAH_TTE,
   - tanggal_tte terisi otomatis.

3. PDF hasil generate SIP Kendaraan tidak lagi menampilkan tulisan:
   - (TTE BSrE)
   pada kolom pemegang SIP maupun pejabat penandatangan.

4. Label dan pesan tampilan terkait upload TTE disederhanakan menjadi TTE, tanpa teks BSrE pada form/preview SIP Kendaraan.

Tidak ada perubahan struktur database/model field baru, sehingga tidak perlu makemigrations.
Setelah ekstrak ZIP, cukup restart server Django.
