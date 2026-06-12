from django import forms
from core.access import filter_form_fields_by_user
from django.core.exceptions import ValidationError

from .models import SIPRumahDinas


def validate_pdf_file(uploaded_file):
    if not uploaded_file:
        return

    filename = uploaded_file.name.lower()

    if not filename.endswith('.pdf'):
        raise ValidationError('Dokumen SIP Rumah Negara hanya boleh berupa file PDF.')

    content_type = getattr(uploaded_file, 'content_type', '')

    if content_type and content_type not in ['application/pdf', 'application/x-pdf']:
        raise ValidationError('Format file tidak valid. Upload dokumen dalam format PDF.')


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user is not None:
            filter_form_fields_by_user(self, self.user)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class SIPRumahDinasForm(BootstrapModelForm):
    class Meta:
        model = SIPRumahDinas

        # dokumen_bast sengaja tidak ditampilkan
        exclude = ['dibuat_oleh', 'dokumen_bast']

        labels = {
            'nomor_sip': 'Nomor SIP',
            'tanggal_sip': 'Tanggal SIP',
            'rumah_dinas': 'Rumah Negara',
            'pegawai': 'Pemegang SIP',
            'penghuni': 'Penghuni Aktual',
            'status_bayar_pnbp': 'Status Bayar Sewa PNBP',
            'tahun_pnbp': 'Tahun PNBP',
            'nilai_pnbp': 'Nilai Sewa PNBP',
            'tanggal_bayar_pnbp': 'Tanggal Bayar PNBP',
            'bukti_bayar_pnbp': 'Bukti Bayar PNBP',
            'tanggal_mulai': 'Tanggal Mulai',
            'tanggal_akhir': 'Tanggal Akhir',
            'dasar_penerbitan': 'Dasar Penerbitan',
            'pejabat_penandatangan': 'Pejabat Penandatangan',
            'jumlah_anggota_keluarga': 'Jumlah Anggota Keluarga',
            'status': 'Status',
            'dokumen_sip': 'Dokumen SIP Rumah Negara (PDF)',
            'catatan': 'Catatan',
        }

        widgets = {
            'tanggal_sip': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'tanggal_mulai': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'tanggal_akhir': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'tanggal_bayar_pnbp': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'dokumen_sip': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,.pdf',
                'class': 'form-control'
            }),
        }

    def clean_dokumen_sip(self):
        dokumen = self.cleaned_data.get('dokumen_sip')

        if not dokumen:
            return dokumen

        validate_pdf_file(dokumen)
        return dokumen

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in ['tanggal_sip', 'tanggal_mulai', 'tanggal_akhir', 'tanggal_bayar_pnbp']:
            value = getattr(self.instance, field_name, None)

            if self.instance and self.instance.pk and value:
                self.fields[field_name].initial = value.strftime('%Y-%m-%d')