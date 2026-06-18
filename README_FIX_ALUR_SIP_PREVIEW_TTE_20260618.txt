PERBAIKAN ALUR SIP KENDARAAN / RUMAH NEGARA - 18 JUNI 2026

1. SIP Kendaraan
   - Generate SIP Kendaraan hanya dilakukan oleh role Pengelola BMN.
   - Alur Pengelola BMN: pilih kendaraan -> sistem otomatis mengisi data dari Master Kendaraan -> isi pengguna kendaraan, masa berlaku SIP, dan data pendukung -> klik Buat/Generate SIP Kendaraan.
   - Jenis kendaraan otomatis mengikuti Master Kendaraan.
   - Kode Barang dan NUP ditampilkan otomatis dari Master Kendaraan dan tidak diinput manual pada form SIP.
   - Saat SIP disimpan/diperbarui pada status Draft/Ditolak, sistem otomatis generate konsep PDF.
   - Konsep PDF ditampilkan sebagai preview di bawah halaman form/detail.
   - Pengelola BMN meneruskan konsep PDF kepada pejabat penerbit sesuai unit kerja: Kepala Biro Umum/Sekretaris/Kepala Balai/Kepala Sentra.
   - Pejabat penerbit melihat preview PDF pada halaman detail persetujuan.
   - Setelah disetujui, pejabat penerbit mengupload dokumen PDF final yang sudah TTE Elektronik/BSrE dari halaman akses pejabat.

2. SIP Rumah Negara
   - Alur disamakan: Pengelola BMN membuat/generate konsep PDF setelah mengisi form.
   - Preview PDF tampil di bawah halaman form/detail.
   - Sekretaris Jenderal melihat preview PDF pada halaman detail persetujuan.
   - Dokumen final TTE Elektronik/BSrE diupload melalui akses Sekretaris Jenderal.

3. Perubahan teknis utama
   - kendaraan/forms.py: field readonly otomatis untuk Jenis Kendaraan, Kode Barang, dan NUP dari Master Kendaraan; jenis_pemakaian disimpan sebagai snapshot sistem.
   - kendaraan/views.py: create/update otomatis generate konsep PDF dan redirect ke detail; pengajuan tidak lagi dipaksa upload TTE calon pemegang terlebih dahulu; upload final TTE tetap di role pejabat penerbit.
   - templates/kendaraan/sip_form.html: preview PDF di bawah halaman dan JavaScript auto-fill data Master Kendaraan.
   - rumah_dinas/views.py dan templates/rumah_dinas/form.html: create/update otomatis generate konsep PDF dan preview PDF di bawah halaman.
