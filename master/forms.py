from django import forms
from .models import UnitKerja, Pegawai, Kendaraan, RumahDinas
from core.access import filter_form_fields_by_user, is_biro_umum_user, get_user_unit_id


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class BootstrapModelForm(forms.ModelForm):
    def _validate_pdf_file(self, uploaded_file, field_label):
        if not uploaded_file:
            return uploaded_file

        filename = (uploaded_file.name or '').lower()
        content_type = getattr(uploaded_file, 'content_type', '')

        if not filename.endswith('.pdf'):
            raise forms.ValidationError(f'{field_label} harus berformat PDF.')

        if content_type and content_type not in ['application/pdf', 'application/x-pdf', 'application/octet-stream']:
            raise forms.ValidationError(f'{field_label} harus berformat PDF.')

        return uploaded_file

    def clean_dokumen_stnk(self):
        return self._validate_pdf_file(self.cleaned_data.get('dokumen_stnk'), 'Dokumen STNK')

    def clean_dokumen_bpkb(self):
        return self._validate_pdf_file(self.cleaned_data.get('dokumen_bpkb'), 'Dokumen BPKB')

    def clean_dokumen_sertifikat(self):
        return self._validate_pdf_file(self.cleaned_data.get('dokumen_sertifikat'), 'Dokumen Sertifikat Rumah Negara')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user is not None:
            filter_form_fields_by_user(self, self.user)

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select) and name in ['unit_kerja', 'pengguna']:
                field.widget.attrs.update({'class': 'form-control searchable-select'})
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class UnitKerjaForm(BootstrapModelForm):
    class Meta:
        model = UnitKerja
        fields = '__all__'


class PegawaiForm(BootstrapModelForm):
    class Meta:
        model = Pegawai
        fields = '__all__'


class KendaraanForm(BootstrapModelForm):
    masa_berlaku_stnk = forms.DateField(
        required=False,
        label='Masa Berlaku STNK',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )

    jatuh_tempo_pajak = forms.DateField(
        required=False,
        label='Jatuh Tempo Pajak',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )

    dokumen_stnk = forms.FileField(
        required=False,
        label='Upload STNK (PDF)',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'application/pdf,.pdf',
            'class': 'form-control'
        }),
        help_text='Upload dokumen STNK dalam format PDF.'
    )

    dokumen_bpkb = forms.FileField(
        required=False,
        label='Upload BPKB (PDF)',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'application/pdf,.pdf',
            'class': 'form-control'
        }),
        help_text='Upload dokumen BPKB dalam format PDF.'
    )

    foto_kendaraan = MultipleImageField(
        required=False,
        label='Upload Foto Kendaraan',
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': 'image/*',
            'class': 'form-control'
        }),
        help_text='Bisa pilih lebih dari satu foto kendaraan sekaligus.'
    )

    class Meta:
        model = Kendaraan
        exclude = ['foto']

        labels = {
            'kode_kendaraan': 'Kode Kendaraan',
            'nomor_polisi': 'Nomor Polisi',
            'nomor_rangka': 'Nomor Rangka',
            'nomor_mesin': 'Nomor Mesin',
            'nomor_bpkb': 'Nomor BPKB',
            'nomor_stnk': 'Nomor STNK',
            'dokumen_stnk': 'Dokumen STNK (PDF)',
            'dokumen_bpkb': 'Dokumen BPKB (PDF)',
            'masa_berlaku_stnk': 'Masa Berlaku STNK',
            'jatuh_tempo_pajak': 'Jatuh Tempo Pajak',
            'nup': 'NUP',
            'kode_barang': 'Kode Barang',
            'nilai_perolehan': 'Nilai Perolehan',
            'unit_kerja': 'Unit Kerja',
            'pengguna': 'Pengguna',
            'jenis_kendaraan': 'Jenis Kendaraan',
            'status_pemanfaatan': 'Status Pemanfaatan',
            'kilometer_terakhir': 'Kilometer Terakhir',
            'keterangan_status_pemanfaatan': 'Keterangan Status Pemanfaatan',
        }

        widgets = {
            'unit_kerja': forms.Select(attrs={
                'class': 'form-control searchable-select',
                'data-placeholder': 'Cari unit kerja...'
            }),
            'pengguna': forms.Select(attrs={
                'class': 'form-control searchable-select',
                'data-placeholder': 'Cari nama/NIP pegawai...'
            }),
        }

    def _validate_pdf_file(self, uploaded_file, field_label):
        if not uploaded_file:
            return uploaded_file

        filename = (uploaded_file.name or '').lower()
        content_type = getattr(uploaded_file, 'content_type', '')

        if not filename.endswith('.pdf'):
            raise forms.ValidationError(f'{field_label} harus berformat PDF.')

        if content_type and content_type not in ['application/pdf', 'application/x-pdf', 'application/octet-stream']:
            raise forms.ValidationError(f'{field_label} harus berformat PDF.')

        return uploaded_file

    def clean_dokumen_stnk(self):
        return self._validate_pdf_file(self.cleaned_data.get('dokumen_stnk'), 'Dokumen STNK')

    def clean_dokumen_bpkb(self):
        return self._validate_pdf_file(self.cleaned_data.get('dokumen_bpkb'), 'Dokumen BPKB')

    def clean_dokumen_sertifikat(self):
        return self._validate_pdf_file(self.cleaned_data.get('dokumen_sertifikat'), 'Dokumen Sertifikat Rumah Negara')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.order_fields([
            'kode_kendaraan', 'nomor_polisi', 'merek', 'tipe', 'jenis_kendaraan',
            'tahun_pembuatan', 'tahun_perolehan', 'warna', 'nomor_rangka', 'nomor_mesin',
            'nomor_bpkb', 'dokumen_bpkb', 'nomor_stnk', 'dokumen_stnk',
            'masa_berlaku_stnk', 'jatuh_tempo_pajak', 'nup', 'kode_barang',
            'nilai_perolehan', 'unit_kerja', 'pengguna', 'kondisi', 'status_pemanfaatan',
            'kilometer_terakhir', 'keterangan_status_pemanfaatan', 'foto_kendaraan'
        ])

        if self.instance and self.instance.pk:
            if self.instance.masa_berlaku_stnk:
                self.fields['masa_berlaku_stnk'].initial = self.instance.masa_berlaku_stnk.strftime('%Y-%m-%d')

            if self.instance.jatuh_tempo_pajak:
                self.fields['jatuh_tempo_pajak'].initial = self.instance.jatuh_tempo_pajak.strftime('%Y-%m-%d')
class RumahDinasForm(BootstrapModelForm):
    dokumen_sertifikat = forms.FileField(
        required=False,
        label='Upload Sertifikat Rumah Negara (PDF)',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'application/pdf,.pdf',
            'class': 'form-control'
        }),
        help_text='Upload sertifikat rumah negara dalam format PDF.'
    )

    foto_rumah_dinas = MultipleImageField(
        required=False,
        label='Upload Foto Rumah Negara',
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': 'image/*',
            'class': 'form-control'
        }),
        help_text='Bisa pilih lebih dari satu foto rumah negara sekaligus.'
    )

    class Meta:
        model = RumahDinas
        exclude = ['foto_depan']
        labels = {
            'nup': 'NUP',
            'kode_barang': 'Kode Barang',
            'kode_rumah': 'Kode Rumah',
            'nama_rumah': 'Nama Rumah Negara',
            'dokumen_sertifikat': 'Sertifikat Rumah Negara (PDF)',
            'unit_kerja': 'Unit Kerja/Satker',
            'status_pemanfaatan': 'Status Pemanfaatan',
            'keterangan_status_pemanfaatan': 'Keterangan Status Pemanfaatan',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields([
            'kode_rumah', 'nama_rumah', 'jenis_rumah', 'alamat',
            'provinsi', 'kabupaten_kota', 'kecamatan', 'kelurahan',
            'latitude', 'longitude', 'luas_tanah', 'luas_bangunan',
            'jumlah_kamar_tidur', 'jumlah_kamar_mandi', 'daya_listrik',
            'tahun_dibangun', 'tahun_perolehan', 'nup', 'kode_barang',
            'nilai_perolehan', 'unit_kerja', 'nomor_sertifikat', 'dokumen_sertifikat',
            'status_tanah', 'kondisi', 'status_pemanfaatan',
            'keterangan_status_pemanfaatan', 'foto_rumah_dinas'
        ])

