# Perbaikan SIKARIS - Generate Konsep PDF SIP dan Persetujuan Sekjen

Perubahan utama:

1. SIP Kendaraan dapat generate Konsep PDF mengikuti format Surat Izin Penunjukan Pemakai Kendaraan Dinas Roda Empat.
2. SIP Kendaraan ditambahkan masa berlaku SIP melalui tanggal mulai/tanggal akhir dan keterangan masa berlaku.
3. SIP Rumah Negara dapat generate Konsep PDF mengikuti format Surat Izin Penghunian Rumah Negara.
4. SIP Rumah Negara ditambahkan jenis masa berlaku: berdasarkan tanggal atau selama masih menduduki jabatan.
5. Ditambahkan role baru: `Sekretaris Jenderal`.
6. Ditambahkan menu Persetujuan Sekjen untuk review SIP Kendaraan dan SIP Rumah Negara.
7. Sekjen/Admin System dapat menyetujui atau menolak SIP yang diajukan.
8. Setelah disetujui, sistem membuat PDF Final dan mengubah status menjadi `MENUNGGU_TTE` untuk proses BSrE/BeSign.
9. Jika ditolak, catatan penolakan wajib diisi.

Langkah setelah update:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # jika belum ada user admin
```

Role `Sekretaris Jenderal` otomatis dibuat oleh migration `accounts/0003_create_sekjen_group.py`. Tambahkan user Sekjen ke group tersebut melalui menu Admin/User Role.

Alur penggunaan:

1. Biro Umum/Admin membuat data SIP.
2. Klik `Generate Konsep PDF` pada detail SIP.
3. Klik `Ajukan ke Sekjen`.
4. User dengan role `Sekretaris Jenderal` membuka menu Persetujuan Sekjen.
5. Sekjen melakukan preview PDF, lalu klik `Setujui SIP` atau isi catatan dan klik `Tolak SIP`.
6. Jika disetujui, PDF final dibuat dan dapat diproses TTE BSrE/BeSign.
