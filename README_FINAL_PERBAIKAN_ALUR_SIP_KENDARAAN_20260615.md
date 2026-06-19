# Perbaikan Final Alur SIP Kendaraan SIM Pengelolaan BMN

Perbaikan ini menyesuaikan alur proses bisnis terakhir:

1. Pengelola BMN hanya membuat Draft/Konsep SIP Kendaraan dan mengajukan.
2. Pengelola BMN tidak dapat menyetujui, menolak, menerbitkan, atau upload dokumen TTE BSrE.
3. Unit di bawah Sekretariat Jenderal diajukan ke Kepala Biro Umum.
4. Unit Eselon I selain Sekretariat Jenderal diajukan ke Sekretaris UKE I/UKE II masing-masing.
5. Sentra diajukan ke Kepala Sentra masing-masing.
6. Balai diajukan ke Kepala Balai masing-masing.
7. Kepala Biro Umum hanya melihat pengajuan dari unit di bawah Sekretariat Jenderal.
8. Sekretaris UKE I/UKE II hanya melihat pengajuan dari unit di bawah Eselon I-nya.
9. Kepala Sentra/Balai hanya melihat pengajuan dari Sentra/Balai masing-masing.
10. Pejabat penerbit dapat generate draft PDF dan upload PDF final yang sudah TTE BSrE.
11. PDF hasil generate tidak lagi menampilkan teks watermark konsep/belum disetujui.
12. Pejabat penerbit pada PDF diambil dari snapshot SIP yang disinkronkan dari Master Unit Kerja.

Perintah setelah ekstrak:

```bash
python3 manage.py migrate
python3 manage.py fix_snapshot_penerbit_sip_kendaraan --force
python3 manage.py runserver
```
