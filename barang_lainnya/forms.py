from django import forms
from django.forms import inlineformset_factory

from master.models import Pegawai
from .models import SIPBarangLainnya, SIPBarangLainnyaItem


class SIPBarangLainnyaForm(forms.ModelForm):
    class Meta:
        model = SIPBarangLainnya
        fields = [
            'nomor_sip', 'tanggal_sip', 'pemegang_sip', 'pengguna_aktual',
            'tanggal_mulai', 'tanggal_akhir', 'dasar_penerbitan', 'tujuan_penggunaan',
            'lokasi_penggunaan', 'pejabat_penandatangan', 'keterangan_tambahan',
            'dokumen_pendukung', 'file_signed_pdf',
        ]
        labels = {
            'pemegang_sip': 'Pemegang SIP',
            'pengguna_aktual': 'Pengguna Aktual',
            'tanggal_mulai': 'Tanggal Mulai',
            'tanggal_akhir': 'Tanggal Akhir',
            'file_signed_pdf': 'Upload SIP yang sudah TTE (Opsional)',
            'keterangan_tambahan': 'Keterangan Tambahan',
            'pejabat_penandatangan': 'Nama Pejabat Penandatangan',
        }
        widgets = {
            'tanggal_sip': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_akhir': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dasar_penerbitan': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'tujuan_penggunaan': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'keterangan_tambahan': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'dokumen_pendukung': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'file_signed_pdf': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if not isinstance(field.widget, forms.FileInput) and not isinstance(field.widget, forms.Textarea) and not isinstance(field.widget, forms.DateInput):
                field.widget.attrs.setdefault('class', 'form-control')
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')
        pegawai_qs = Pegawai.objects.order_by('nama')
        self.fields['pemegang_sip'].queryset = pegawai_qs
        self.fields['pengguna_aktual'].queryset = pegawai_qs
        self.fields['pejabat_penandatangan'].queryset = pegawai_qs
        self.fields['nomor_sip'].required = True
        self.fields['nomor_sip'].help_text = 'Nomor SIP diinput manual oleh pengguna, tidak dibuat otomatis.'


class SIPBarangLainnyaItemForm(forms.ModelForm):
    class Meta:
        model = SIPBarangLainnyaItem
        fields = ['urutan', 'nama_barang', 'spesifikasi', 'satuan', 'jumlah', 'nup', 'serial_number', 'keterangan']
        widgets = {
            'urutan': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'nama_barang': forms.TextInput(attrs={'class': 'form-control'}),
            'spesifikasi': forms.TextInput(attrs={'class': 'form-control'}),
            'satuan': forms.TextInput(attrs={'class': 'form-control'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'nup': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opsional'}),
            'keterangan': forms.TextInput(attrs={'class': 'form-control'}),
        }


SIPBarangLainnyaItemFormSet = inlineformset_factory(
    SIPBarangLainnya,
    SIPBarangLainnyaItem,
    form=SIPBarangLainnyaItemForm,
    extra=3,
    can_delete=True,
)
