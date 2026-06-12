from django import forms
from django.utils import timezone

from core.access import get_user_unit_kerja, is_biro_umum_user
from master.models import Kendaraan, Pegawai, RumahDinas, UnitKerja
from tanah_negara.models import TanahNegara
from .models import PermohonanPSPBMN


FILE_ACCEPT = 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx'


class PermohonanPSPBMNForm(forms.ModelForm):
    class Meta:
        model = PermohonanPSPBMN
        fields = [
            'tanggal_permohonan', 'unit_kerja', 'pemohon', 'jenis_barang',
            'kendaraan', 'rumah_negara', 'tanah_negara',
            'kode_barang', 'nup', 'nama_barang', 'nilai_psp', 'kondisi_barang',
            'lokasi_barang', 'keterangan_barang',
            'surat_permohonan_satker', 'surat_pengantar_eselon1',
            'daftar_kondisi_barang', 'laporan_sub_kelompok_barang',
            'surat_pernyataan_kepala_satker',
            'foto_kendaraan', 'dokumen_kepemilikan',
            'surat_pernyataan_pengganti_kepemilikan',
            'status', 'catatan_unit', 'catatan_biro_umum',
            'nomor_penetapan_psp', 'tanggal_penetapan_psp', 'dokumen_penetapan_psp',
        ]
        labels = {
            'tanggal_permohonan': 'Tanggal Permohonan',
            'unit_kerja': 'Unit Kerja/Satker Pemohon',
            'pemohon': 'Pegawai Pemohon/PIC Unit Kerja',
            'jenis_barang': 'Jenis Barang/Aset BMN',
            'rumah_negara': 'Rumah Negara',
            'tanah_negara': 'Tanah Negara',
            'kode_barang': 'Kode Barang',
            'nup': 'NUP',
            'nama_barang': 'Nama Barang/Aset',
            'nilai_psp': 'Nilai PSP/Nilai Perolehan',
            'kondisi_barang': 'Kondisi Barang',
            'lokasi_barang': 'Lokasi Barang',
            'keterangan_barang': 'Keterangan Barang',
            'surat_permohonan_satker': 'Surat Permohonan dari Satker',
            'surat_pengantar_eselon1': 'Surat Pengantar/Usulan dari Eselon I',
            'daftar_kondisi_barang': 'Daftar Kondisi Barang',
            'laporan_sub_kelompok_barang': 'Laporan Sub Kelompok Barang',
            'surat_pernyataan_kepala_satker': 'Surat Pernyataan Kepala Satker',
            'foto_kendaraan': 'Foto Kendaraan',
            'dokumen_kepemilikan': 'Dokumen Kepemilikan Kendaraan (BPKB/STNK/dokumen lain)',
            'surat_pernyataan_pengganti_kepemilikan': 'Surat Pernyataan Pengganti Dokumen Kepemilikan',
            'status': 'Status Permohonan',
            'catatan_unit': 'Catatan Unit Kerja',
            'catatan_biro_umum': 'Catatan Biro Umum',
            'nomor_penetapan_psp': 'Nomor Penetapan PSP',
            'tanggal_penetapan_psp': 'Tanggal Penetapan PSP',
            'dokumen_penetapan_psp': 'Dokumen Penetapan PSP',
        }
        help_texts = {
            'nilai_psp': 'Jika jenis barang kendaraan dan nilai lebih dari Rp100 juta, foto kendaraan dan dokumen kepemilikan/surat pernyataan pengganti menjadi wajib.',
            'dokumen_kepemilikan': 'Contoh: BPKB, STNK, atau dokumen pendukung lain.',
            'surat_pernyataan_pengganti_kepemilikan': 'Diisi jika dokumen kepemilikan kendaraan tidak tersedia.',
        }
        widgets = {
            'tanggal_permohonan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_penetapan_psp': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'lokasi_barang': forms.Textarea(attrs={'rows': 2}),
            'keterangan_barang': forms.Textarea(attrs={'rows': 3}),
            'catatan_unit': forms.Textarea(attrs={'rows': 3}),
            'catatan_biro_umum': forms.Textarea(attrs={'rows': 3}),
            'surat_permohonan_satker': forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT}),
            'surat_pengantar_eselon1': forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT}),
            'daftar_kondisi_barang': forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT}),
            'laporan_sub_kelompok_barang': forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT}),
            'surat_pernyataan_kepala_satker': forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT}),
            'foto_kendaraan': forms.ClearableFileInput(attrs={'accept': 'image/*,.jpg,.jpeg,.png,.pdf'}),
            'dokumen_kepemilikan': forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT}),
            'surat_pernyataan_pengganti_kepemilikan': forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT}),
            'dokumen_penetapan_psp': forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})

        self.fields['kendaraan'].required = False
        self.fields['rumah_negara'].required = False
        self.fields['tanah_negara'].required = False
        self.fields['unit_kerja'].queryset = UnitKerja.objects.order_by('nama_unit')
        self.fields['pemohon'].queryset = Pegawai.objects.select_related('unit_kerja').order_by('nama')
        self.fields['kendaraan'].queryset = Kendaraan.objects.select_related('unit_kerja').order_by('nomor_polisi')
        self.fields['rumah_negara'].queryset = RumahDinas.objects.select_related('unit_kerja').order_by('kode_rumah')
        self.fields['tanah_negara'].queryset = TanahNegara.objects.select_related('unit_kerja').order_by('kode_tanah')

        if self.user and not is_biro_umum_user(self.user):
            unit = get_user_unit_kerja(self.user)
            if unit:
                self.fields['unit_kerja'].queryset = UnitKerja.objects.filter(pk=unit.pk)
                self.fields['unit_kerja'].initial = unit.pk
                self.fields['pemohon'].queryset = Pegawai.objects.filter(unit_kerja=unit).order_by('nama')
                self.fields['kendaraan'].queryset = Kendaraan.objects.filter(unit_kerja=unit).order_by('nomor_polisi')
                self.fields['rumah_negara'].queryset = RumahDinas.objects.filter(unit_kerja=unit).order_by('kode_rumah')
                self.fields['tanah_negara'].queryset = TanahNegara.objects.filter(unit_kerja=unit).order_by('kode_tanah')

            biro_only_fields = ['status', 'catatan_biro_umum', 'nomor_penetapan_psp', 'tanggal_penetapan_psp', 'dokumen_penetapan_psp']
            for field in biro_only_fields:
                self.fields.pop(field, None)
        else:
            self.fields['status'].help_text = 'Status ini dikelola Biro Umum setelah permohonan diajukan unit kerja.'

        if self.instance and self.instance.pk:
            for date_field in ['tanggal_permohonan', 'tanggal_penetapan_psp']:
                value = getattr(self.instance, date_field, None)
                if value and date_field in self.fields:
                    self.fields[date_field].initial = value.strftime('%Y-%m-%d')

    def _has_file(self, field_name):
        new_file = self.cleaned_data.get(field_name)
        old_file = getattr(self.instance, field_name, None)
        return bool(new_file or old_file)

    def clean(self):
        cleaned = super().clean()
        jenis = cleaned.get('jenis_barang')
        nilai = cleaned.get('nilai_psp') or 0

        if jenis == 'KENDARAAN' and not cleaned.get('kendaraan'):
            raise forms.ValidationError('Untuk jenis barang Kendaraan, pilih data kendaraan yang diajukan PSP.')
        if jenis == 'RUMAH_NEGARA' and not cleaned.get('rumah_negara'):
            raise forms.ValidationError('Untuk jenis barang Rumah Negara, pilih data rumah negara yang diajukan PSP.')
        if jenis == 'TANAH_NEGARA' and not cleaned.get('tanah_negara'):
            raise forms.ValidationError('Untuk jenis barang Tanah Negara, pilih data tanah negara yang diajukan PSP.')

        required_base = [
            ('surat_permohonan_satker', 'Surat permohonan dari Satker'),
            ('surat_pengantar_eselon1', 'Surat pengantar/usulan dari Eselon I'),
            ('daftar_kondisi_barang', 'Daftar kondisi barang'),
            ('laporan_sub_kelompok_barang', 'Laporan sub kelompok barang'),
            ('surat_pernyataan_kepala_satker', 'Surat Pernyataan Kepala Satker'),
        ]
        for field, label in required_base:
            if not self._has_file(field):
                self.add_error(field, f'{label} wajib diunggah untuk pengajuan PSP.')

        if jenis == 'KENDARAAN' and nilai and nilai > 100000000:
            if not self._has_file('foto_kendaraan'):
                self.add_error('foto_kendaraan', 'Foto kendaraan wajib diunggah untuk kendaraan dengan nilai PSP di atas Rp100 juta.')
            if not self._has_file('dokumen_kepemilikan') and not self._has_file('surat_pernyataan_pengganti_kepemilikan'):
                raise forms.ValidationError('Untuk kendaraan dengan nilai PSP di atas Rp100 juta, unggah dokumen kepemilikan kendaraan atau Surat Pernyataan Kepala Satker sebagai pengganti jika dokumen kepemilikan tidak tersedia.')
        return cleaned
