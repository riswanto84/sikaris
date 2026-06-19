# Perbaikan Dokumen PSP Word dan Nama/NIP Pejabat

Perubahan:

1. Generate Dokumen PSP SIM Pengelolaan BMN sekarang menghasilkan file Word `.docx`, bukan PDF, agar dapat diedit sebelum e-Meterai dan TTE BSrE.
   - Nota Dinas PSP
   - Surat Keterangan Kebenaran Dokumen Digital
   - Surat Pernyataan Formil dan Materiil/e-Meterai

2. Nama dan NIP pejabat penandatangan pada dokumen Word tidak lagi mengambil pegawai dummy dari Master Pegawai.
   - Jika `pejabat_tte` dan `nip_pejabat_tte` belum diisi pada data PSP, Word menampilkan garis kosong untuk diisi manual.
   - Ini mencegah kesalahan seperti pegawai dummy tampil sebagai Kepala Biro Umum.

3. Template detail PSP diperbarui agar tombol tertulis Generate Word.

4. Dependency ditambahkan ke `requirements.txt`:
   - python-docx==1.2.0

Setelah ekstrak, jalankan:

```bash
pip install -r requirements.txt
python3 manage.py runserver
```
