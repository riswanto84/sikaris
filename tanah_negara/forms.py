from django import forms
from .models import TanahNegara


class TanahNegaraForm(forms.ModelForm):
    class Meta:
        model = TanahNegara
        exclude = ['dibuat_oleh']
        labels = {
            'kode_tanah': 'Kode Tanah',
            'kode_satker': 'Kode Satker',
            'nama_satker': 'Nama Satker',
            'unit_kerja': 'Unit Kerja/Satker',
            'kode_barang': 'Kode Barang',
            'nup': 'NUP',
            'nama_barang': 'Nama Barang',
            'nama_aset': 'Nama Aset',
            'nama_tanah': 'Nama/Lokasi Tanah Negara',
            'status_bmn': 'Status BMN',
            'kondisi': 'Kondisi',
            'intra_extra': 'Intra/Extra',
            'jenis_dokumen': 'Jenis Dokumen',
            'nomor_dokumen': 'Nomor Dokumen',
            'status_sertifikasi': 'Status Sertifikasi',
            'jenis_sertipikat': 'Jenis Sertipikat',
            'nomor_sertifikat': 'Nomor Sertifikat',
            'atas_nama_sertifikat': 'Atas Nama Sertifikat',
            'tanggal_sertifikat': 'Tanggal Sertifikat',
            'tanggal_buku_pertama': 'Tanggal Buku Pertama',
            'tanggal_perolehan': 'Tanggal Perolehan',
            'nilai_perolehan': 'Nilai Perolehan',
            'nilai_buku': 'Nilai Buku',
            'luas_tanah': 'Luas Tanah Utama (m²)',
            'luas_tanah_seluruhnya': 'Luas Tanah Seluruhnya (m²)',
            'luas_tanah_untuk_bangunan': 'Luas Tanah untuk Bangunan (m²)',
            'luas_tanah_untuk_sarana_lingkungan': 'Luas Tanah untuk Sarana Lingkungan (m²)',
            'luas_lahan_kosong': 'Luas Lahan Kosong (m²)',
            'luas_pemanfaatan': 'Luas Pemanfaatan (m²)',
            'jumlah_foto': 'Jumlah Foto',
            'status_penggunaan': 'Status Penggunaan',
            'status_pemanfaatan': 'Status Pemanfaatan',
            'status_tanah': 'Kategori Status Tanah',
            'no_psp': 'Nomor PSP',
            'tanggal_psp': 'Tanggal PSP',
            'rt_rw': 'RT/RW',
            'kelurahan_desa': 'Kelurahan/Desa',
            'kab_kota': 'Kab/Kota',
            'kode_kab_kota': 'Kode Kab/Kota',
            'kode_provinsi': 'Kode Provinsi',
            'kode_pos': 'Kode Pos',
            'sbsk': 'SBSK',
            'optimalisasi': 'Optimalisasi',
            'penghuni': 'Penghuni',
            'pengguna': 'Pengguna',
            'digunakan_oleh': 'Digunakan Oleh',
            'kode_kpknl': 'Kode KPKNL',
            'uraian_kpknl': 'Uraian KPKNL',
            'uraian_kanwil_djkn': 'Uraian Kanwil DJKN',
            'nama_kl': 'Nama K/L',
            'nama_e1': 'Nama E1',
            'nama_korwil': 'Nama Korwil',
            'kode_register': 'Kode Register',
            'status_pmk': 'Status PMK',
            'dokumen_sertifikat': 'Upload Sertifikat (PDF/Gambar)',
        }
        widgets = {
            'tanggal_sertifikat': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_buku_pertama': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_perolehan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_psp': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'dokumen_sertifikat': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png'}),
            'keterangan': forms.Textarea(attrs={'rows': 4}),
            'alamat': forms.Textarea(attrs={'rows': 3}),
            'jenis_dokumen': forms.Textarea(attrs={'rows': 2}),
            'status_penggunaan': forms.Textarea(attrs={'rows': 2}),
            'status_pemanfaatan': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})
        for field_name in ['tanggal_sertifikat', 'tanggal_buku_pertama', 'tanggal_perolehan', 'tanggal_psp']:
            value = getattr(self.instance, field_name, None)
            if self.instance and self.instance.pk and value:
                self.fields[field_name].initial = value.strftime('%Y-%m-%d')
