# Perbaikan SIKARIS - PSP BMN Banyak Barang, Penomoran Otomatis, TTE BSrE, dan e-Meterai

Tanggal: 15 Juni 2026

## Ringkasan Perbaikan

1. Modul PSP BMN sekarang mendukung **paket usulan banyak barang**.
2. Ditambahkan import Excel lampiran barang PSP dengan kolom:
   - no
   - kode_satuan_kerja
   - nama_satuan_kerja
   - kode_barang
   - nup
   - nama_barang
   - tipe_barang
   - tahun_perolehan
   - kuantitas
   - nilai_perolehan
   - kondisi_barang
   - keterangan
3. Sistem otomatis menghitung:
   - jumlah barang
   - total nilai barang
   - nilai tertinggi per unit
   - indikator barang di atas Rp100.000.000 per unit
4. Ditambahkan nomor tiket SIMAN V2 pada paket PSP.
5. Ditambahkan checklist dokumen PSP:
   - dokumen permohonan PSP gabungan
   - surat permohonan satker
   - surat pengantar eselon I
   - daftar kondisi barang
   - laporan sub-sub kelompok barang
   - surat pernyataan kepala satker
   - dokumen kepemilikan/surat pengganti jika diperlukan
6. Penomoran surat otomatis memakai sequence database:
   - Nota/Surat Biro Umum: `nomor/1.5/PL.04/bulan/tahun`, contoh `536/1.5/PL.04/1/2026`
   - SK PSP: `nomor/HUK/tahun`, contoh `72/HUK/2026`
   - Nomor paket PSP internal: `PSP-BMN/tahun/00001`
7. Ditambahkan model `NomorSuratSequence` pada app `core` agar nomor surat tidak dobel.
8. Ditambahkan kontrol dokumen **TTE BSrE**:
   - status TTE
   - pejabat TTE
   - NIP pejabat TTE
   - tanggal TTE
   - file sebelum TTE
   - file setelah TTE
9. Ditambahkan kontrol **e-Meterai** untuk surat bermeterai:
   - status e-Meterai
   - nomor serial e-Meterai
   - tanggal e-Meterai
   - dokumen bermeterai elektronik
10. SIP Kendaraan dan SIP Rumah Negara dapat mengisi nomor SIP otomatis jika kolom nomor dikosongkan.
    - SIP Kendaraan default pejabat penandatangan: Kepala Biro Umum (TTE BSrE)
    - SIP Rumah Negara default pejabat penandatangan: Sekretaris Jenderal (TTE BSrE)
11. PDF SIP Kendaraan disesuaikan agar persetujuan kendaraan mengarah ke Kepala Biro Umum.
12. Detail PSP memiliki tombol:
    - Import Excel Barang
    - Export Lampiran PDF
13. Disediakan template Excel import barang PSP melalui menu PSP.

## Cara Migrasi

Jalankan perintah berikut setelah menyalin source code ini:

```bash
python manage.py makemigrations
python manage.py migrate
```

Catatan: migrasi manual sudah disiapkan:
- `core/migrations/0001_nomorsuratsequence.py`
- `kendaraan/migrations/0006_nomor_sip_otomatis_tte.py`
- `rumah_dinas/migrations/0004_nomor_sip_otomatis_tte.py`
- `psp/migrations/0003_psp_banyak_barang_nomor_tte.py`

Jika Django meminta konfirmasi migrasi tambahan, jalankan `python manage.py makemigrations` lalu `python manage.py migrate`.

## Catatan TTE BSrE

Aplikasi ini tidak meniru tanda tangan basah/scan. File final disiapkan untuk proses TTE BSrE dan hasil TTE diunggah kembali ke sistem sebagai PDF final.

## Catatan e-Meterai

Surat bermeterai dapat menggunakan e-Meterai resmi pada dokumen elektronik/PDF. e-Meterai dan TTE BSrE sebaiknya diletakkan berdampingan dan tidak saling menimpa agar QR/validasi tetap terbaca.
