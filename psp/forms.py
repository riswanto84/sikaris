from django import forms

from core.access import get_user_unit_kerja, is_biro_umum_user
from master.models import Pegawai, UnitKerja
from .models import PermohonanPSPBMN

PDF_ACCEPT = 'application/pdf,.pdf'


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


def validate_pdf(uploaded_file, label):
    if not uploaded_file:
        return uploaded_file
    if not uploaded_file.name.lower().endswith('.pdf'):
        raise forms.ValidationError(f'{label} harus berformat PDF.')
    return uploaded_file


class PermohonanPSPBMNForm(forms.ModelForm):
    foto_barang_files = MultipleImageField(
        required=False,
        label='Foto Barang',
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*,.jpg,.jpeg,.png', 'class': 'form-control'}),
        help_text='Bisa upload lebih dari satu foto barang/aset.'
    )

    class Meta:
        model = PermohonanPSPBMN
        fields = [
            'tanggal_permohonan', 'unit_kerja', 'pemohon', 'jenis_barang',
            'nilai_psp', 'keterangan_barang', 'dokumen_permohonan_psp',
            'foto_barang_files', 'dokumen_kepemilikan',
            'surat_pernyataan_pengganti_kepemilikan',
            'status', 'catatan_unit', 'catatan_biro_umum',
            'nomor_sk_psp', 'tanggal_sk_psp', 'sk_penetapan_psp',
        ]
        labels = {
            'tanggal_permohonan': 'Tanggal Permohonan',
            'unit_kerja': 'Unit Kerja/Satker Pemohon',
            'pemohon': 'Pegawai Pemohon/PIC Unit Kerja',
            'jenis_barang': 'Jenis Barang/Aset BMN',
            'nilai_psp': 'Nilai PSP/Nilai Perolehan',
            'keterangan_barang': 'Keterangan Barang',
            'dokumen_permohonan_psp': 'Dokumen Permohonan PSP Gabungan (PDF)',
            'foto_barang_files': 'Foto Barang',
            'dokumen_kepemilikan': 'Dokumen Kepemilikan Kendaraan (BPKB/STNK/dokumen lain)',
            'surat_pernyataan_pengganti_kepemilikan': 'Surat Pernyataan Pengganti Dokumen Kepemilikan',
            'status': 'Status Permohonan',
            'catatan_unit': 'Catatan Unit Kerja',
            'catatan_biro_umum': 'Catatan Biro Umum',
            'nomor_sk_psp': 'Nomor SK PSP',
            'tanggal_sk_psp': 'Tanggal SK PSP',
            'sk_penetapan_psp': 'SK Penetapan PSP',
        }
        help_texts = {
            'dokumen_permohonan_psp': 'Gabungkan surat permohonan Satker, pengantar Eselon I, daftar kondisi barang, laporan sub kelompok barang, dan surat pernyataan Kepala Satker menjadi satu file PDF.',
            'nilai_psp': 'Jika jenis barang kendaraan dan nilai lebih dari Rp100 juta, foto barang dan dokumen kepemilikan/surat pernyataan pengganti menjadi wajib.',
            'dokumen_kepemilikan': 'Contoh: BPKB, STNK, atau dokumen pendukung lain.',
            'surat_pernyataan_pengganti_kepemilikan': 'Diisi jika dokumen kepemilikan kendaraan tidak tersedia.',
        }
        widgets = {
            'tanggal_permohonan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_sk_psp': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'keterangan_barang': forms.Textarea(attrs={'rows': 3}),
            'catatan_unit': forms.Textarea(attrs={'rows': 3}),
            'catatan_biro_umum': forms.Textarea(attrs={'rows': 3}),
            'dokumen_permohonan_psp': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
            'dokumen_kepemilikan': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
            'surat_pernyataan_pengganti_kepemilikan': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
            'sk_penetapan_psp': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})

        self.fields['unit_kerja'].queryset = UnitKerja.objects.order_by('nama_unit')
        self.fields['pemohon'].queryset = Pegawai.objects.select_related('unit_kerja').order_by('nama')

        if self.user and not is_biro_umum_user(self.user):
            unit = get_user_unit_kerja(self.user)
            if unit:
                self.fields['unit_kerja'].queryset = UnitKerja.objects.filter(pk=unit.pk)
                self.fields['unit_kerja'].initial = unit.pk
                self.fields['pemohon'].queryset = Pegawai.objects.filter(unit_kerja=unit).order_by('nama')

            biro_only_fields = ['status', 'catatan_biro_umum', 'nomor_sk_psp', 'tanggal_sk_psp', 'sk_penetapan_psp']
            for field in biro_only_fields:
                self.fields.pop(field, None)
        else:
            self.fields['status'].help_text = 'Status ini dikelola Biro Umum setelah permohonan diajukan unit kerja.'

        if self.instance and self.instance.pk:
            for date_field in ['tanggal_permohonan', 'tanggal_sk_psp']:
                value = getattr(self.instance, date_field, None)
                if value and date_field in self.fields:
                    self.fields[date_field].initial = value.strftime('%Y-%m-%d')

    def _has_file(self, field_name):
        new_file = self.cleaned_data.get(field_name)
        old_file = getattr(self.instance, field_name, None)
        return bool(new_file or old_file)

    def clean_dokumen_permohonan_psp(self):
        return validate_pdf(self.cleaned_data.get('dokumen_permohonan_psp'), 'Dokumen permohonan PSP gabungan')

    def clean_dokumen_kepemilikan(self):
        return validate_pdf(self.cleaned_data.get('dokumen_kepemilikan'), 'Dokumen kepemilikan')

    def clean_surat_pernyataan_pengganti_kepemilikan(self):
        return validate_pdf(self.cleaned_data.get('surat_pernyataan_pengganti_kepemilikan'), 'Surat pernyataan pengganti dokumen kepemilikan')

    def clean_sk_penetapan_psp(self):
        return validate_pdf(self.cleaned_data.get('sk_penetapan_psp'), 'SK Penetapan PSP')

    def clean(self):
        cleaned = super().clean()
        jenis = cleaned.get('jenis_barang')
        nilai = cleaned.get('nilai_psp') or 0

        if not self._has_file('dokumen_permohonan_psp'):
            self.add_error('dokumen_permohonan_psp', 'Dokumen permohonan PSP gabungan wajib diunggah dalam format PDF.')

        foto_files = cleaned.get('foto_barang_files') or []
        has_existing_photos = bool(self.instance and self.instance.pk and self.instance.foto_barang_list.exists())
        if jenis == 'KENDARAAN' and nilai and nilai > 100000000:
            if not foto_files and not has_existing_photos:
                self.add_error('foto_barang_files', 'Foto barang wajib diunggah untuk kendaraan dengan nilai PSP di atas Rp100 juta.')
            if not self._has_file('dokumen_kepemilikan') and not self._has_file('surat_pernyataan_pengganti_kepemilikan'):
                raise forms.ValidationError('Untuk kendaraan dengan nilai PSP di atas Rp100 juta, unggah dokumen kepemilikan kendaraan atau Surat Pernyataan Kepala Satker sebagai pengganti jika dokumen kepemilikan tidak tersedia.')
        return cleaned
