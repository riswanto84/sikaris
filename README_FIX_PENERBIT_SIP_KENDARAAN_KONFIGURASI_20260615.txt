PERBAIKAN PENERBIT SIP KENDARAAN

Masalah:
Pada Detail SIP Kendaraan muncul pesan:
"Pejabat penerbit SIP Kendaraan belum dikonfigurasi pada Master Unit Kerja"
padahal Master Unit Kerja, misalnya Biro Umum, sudah diisi pejabat penerbitnya.

Penyebab:
Snapshot pejabat penerbit pada data SIP lama belum otomatis tersinkron setelah Master Unit Kerja diperbarui. Selain itu, penentuan target unit penerbit belum cukup kuat untuk beberapa pola unit kerja lama.

Perbaikan:
1. Logika kendaraan/sip_penerbit.py diperkuat:
   - Unit di bawah Setjen otomatis diarahkan ke Biro Umum.
   - Sentra/Balai tetap diarahkan ke unit masing-masing.
   - Eselon I selain Setjen diarahkan ke Sekretariat UKE I masing-masing.
   - Jika target unit belum lengkap tetapi unit sumber sudah punya pejabat penerbit, sistem memakai fallback aman.

2. Detail SIP Kendaraan otomatis menyinkronkan snapshot pejabat penerbit jika masih kosong.

3. Ditambahkan command:
   python3 manage.py fix_snapshot_penerbit_sip_kendaraan --force

Cara pakai setelah ekstrak ZIP:
1. Jalankan migrasi jika belum:
   python3 manage.py migrate

2. Pastikan Master Unit Kerja sudah berisi:
   - jenis unit
   - pejabat penerbit SIP kendaraan
   - nama jabatan penerbit SIP kendaraan

3. Jalankan sinkronisasi snapshot:
   python3 manage.py fix_snapshot_penerbit_sip_kendaraan --force

4. Jalankan aplikasi:
   python3 manage.py runserver
