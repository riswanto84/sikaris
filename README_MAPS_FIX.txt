SIKARIS - Perbaikan Google Maps Rumah Dinas

Perubahan:
1. templates/master/rumah_form.html diperbarui agar menampilkan Google Maps di bawah foto rumah dinas.
2. Peta mengambil koordinat dari field latitude dan longitude.
3. Jika koordinat belum valid, halaman menampilkan pesan agar latitude/longitude diisi.
4. master/views.py tetap memakai RumahDinasPhotoMixin dengan template_name = 'master/rumah_form.html'.
5. settings.py ditambahkan X_FRAME_OPTIONS = 'SAMEORIGIN' jika belum ada.

Cara menjalankan:
python manage.py runserver

Buka:
http://localhost:8000/master/rumah-dinas/1/edit/

Catatan:
Pastikan data Rumah Dinas memiliki latitude dan longitude yang valid, contoh:
latitude = -6.237964898327056
longitude = 106.91559847626894
