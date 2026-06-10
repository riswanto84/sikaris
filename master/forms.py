from django import forms
from .models import UnitKerja, Pegawai, Kendaraan, RumahDinas


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            if self.instance.masa_berlaku_stnk:
                self.fields['masa_berlaku_stnk'].initial = self.instance.masa_berlaku_stnk.strftime('%Y-%m-%d')

            if self.instance.jatuh_tempo_pajak:
                self.fields['jatuh_tempo_pajak'].initial = self.instance.jatuh_tempo_pajak.strftime('%Y-%m-%d')
class RumahDinasForm(BootstrapModelForm):
    foto_rumah_dinas = MultipleImageField(
        required=False,
        label='Upload Foto Rumah Dinas',
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': 'image/*',
            'class': 'form-control'
        }),
        help_text='Bisa pilih lebih dari satu foto rumah dinas sekaligus.'
    )

    class Meta:
        model = RumahDinas
        exclude = ['foto_depan']
        labels = {
            'nup': 'NUP',
            'kode_barang': 'Kode Barang',
            'kode_rumah': 'Kode Rumah',
            'nama_rumah': 'Nama Rumah Dinas',
        }
