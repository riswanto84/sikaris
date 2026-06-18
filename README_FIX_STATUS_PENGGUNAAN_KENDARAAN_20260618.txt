Perbaikan status penggunaan kendaraan:

1. Field database master.Kendaraan yang sebelumnya status_pemanfaatan diubah menjadi status_penggunaan.
2. Pilihan status penggunaan kendaraan disesuaikan dengan daftar SIMAN:
   - -
   - Digunakan sendiri untuk dinas jabatan
   - Digunakan sendiri untuk operasional
   - Digunakan oleh satker lain dalam satu Kementerian/ Lembaga (K/L)
   - Digunakan oleh satker lain diluar Kementerian/ Lembaga (K/L)
   - Digunakan Pihak Lain Sesuai Ketentuan
   - BMN Tidak Digunakan
   - Digunakan Pihak Lain
   - Digunakan Pihak Lain Tidak Sesuai Prosedur
   - Digunakan sendiri untuk kendaraan fungsional
3. Import SIMAN menerima kolom status_penggunaan atau status_pemanfaatan, lalu menormalisasi ke pilihan status penggunaan baru.
4. List, laporan, admin, form, dan export kendaraan diarahkan memakai status_penggunaan.
5. Migration baru: master/migrations/0012_rename_kendaraan_status_penggunaan.py
