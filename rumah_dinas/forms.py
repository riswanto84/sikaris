from django import forms
from core.access import filter_form_fields_by_user
from django.core.exceptions import ValidationError

from .models import SIPRumahDinas
from master.models import Pegawai
from django.utils import timezone


def validate_pdf_file(uploaded_file):
    if not uploaded_file:
        return

    filename = uploaded_file.name.lower()

    if not filename.endswith('.pdf'):
        raise ValidationError('Dokumen SIP Rumah Negara hanya boleh berupa file PDF.')

    content_type = getattr(uploaded_file, 'content_type', '')

    if content_type and content_type not in ['application/pdf', 'application/x-pdf']:
        raise ValidationError('Format file tidak valid. Upload dokumen dalam format PDF.')


def validate_dokumen_lainnya_file(uploaded_file):
    if not uploaded_file:
        return

    filename = uploaded_file.name.lower()
    allowed_extensions = (
        '.pdf', '.jpg', '.jpeg', '.png', '.webp',
        '.doc', '.docx', '.xls', '.xlsx'
    )
    if not filename.endswith(allowed_extensions):
        raise ValidationError(
            'Dokumen lainnya hanya boleh berupa PDF, JPG, JPEG, PNG, WEBP, DOC, DOCX, XLS, atau XLSX.'
        )


class BootstrapModelForm(forms.ModelForm):
    def clean(self):
        cleaned = super().clean()

        # Samakan dengan SIP Kendaraan: status tidak diubah dari form.
        # Edit hanya boleh saat Draft/Konsep atau Ditolak.
        if self.instance and self.instance.pk:
            status = getattr(self.instance, 'status', 'DRAFT')
            if status not in ['DRAFT', 'DITOLAK'] and not (self.user and self.user.is_superuser):
                raise ValidationError('SIP Rumah Negara hanya dapat diedit saat berstatus Draft/Konsep atau Ditolak.')

        return cleaned

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user is not None:
            filter_form_fields_by_user(self, self.user)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class SIPRumahDinasForm(BootstrapModelForm):
    jabatan_pejabat_penandatangan_display = forms.CharField(
        label='Jabatan Pejabat Penandatangan',
        required=False,
        disabled=True,
        help_text='Otomatis dari Master Pegawai berdasarkan nama pejabat penandatangan yang dipilih. Field ini tidak dapat diedit manual.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'placeholder': 'Otomatis dari Master Pegawai'
        })
    )

    class Meta:
        model = SIPRumahDinas

        # dokumen_bast dan field teknis workflow sengaja tidak ditampilkan.
        # Nama pejabat penandatangan dan file SIP final TTE ditampilkan untuk role Pengelola BMN.
        exclude = [
            'dibuat_oleh', 'dokumen_bast', 'dokumen_sip', 'status', 'file_konsep_pdf',
            'pejabat_penandatangan',
            'file_tte_calon_pengguna', 'status_tte_calon_pengguna', 'tanggal_tte_calon_pengguna',
            'catatan_tte_calon_pengguna', 'file_final_pdf', 'status_tte', 'tanggal_tte',
            'catatan_tte', 'tanggal_pengajuan', 'tanggal_persetujuan', 'disetujui_oleh',
            'catatan_penolakan', 'nama_pejabat_penandatangan', 'nip_pejabat_penandatangan',
            'jabatan_pejabat_penandatangan'
        ]

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
            'tanggal_mulai': 'Tanggal Mulai SIP',
            'tanggal_akhir': 'Tanggal Akhir SIP',
            'jenis_masa_berlaku': 'Jenis Masa Berlaku SIP',
            'masa_berlaku_sip': 'Keterangan Masa Berlaku SIP',
            'dasar_penerbitan': 'Dasar Penerbitan',
            'pejabat_penandatangan_pegawai': 'Nama Pejabat Penandatangan',
            'jabatan_pejabat_penandatangan_display': 'Jabatan Pejabat Penandatangan',
            'file_signed_pdf': 'Upload SIP Rumah Negara yang sudah TTE',
            'jumlah_anggota_keluarga': 'Jumlah Anggota Keluarga',
            'status': 'Status',
            'dokumen_sip': 'Dokumen SIP Rumah Negara (PDF)',
            'dokumen_lainnya': 'Dokumen Lainnya / Lampiran Pendukung (Opsional)',
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
            'file_signed_pdf': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,.pdf',
                'class': 'form-control'
            }),
            'dokumen_lainnya': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,.pdf,image/*,.jpg,.jpeg,.png,.webp,.doc,.docx,.xls,.xlsx',
                'class': 'form-control'
            }),
        }

    def clean_dokumen_lainnya(self):
        dokumen = self.cleaned_data.get('dokumen_lainnya')
        if not dokumen:
            return dokumen
        validate_dokumen_lainnya_file(dokumen)
        return dokumen

    def clean_dokumen_sip(self):
        dokumen = self.cleaned_data.get('dokumen_sip')

        if not dokumen:
            return dokumen

        validate_pdf_file(dokumen)
        return dokumen

    def clean_file_signed_pdf(self):
        dokumen = self.cleaned_data.get('file_signed_pdf')
        if not dokumen:
            return dokumen
        validate_pdf_file(dokumen)
        return dokumen

    def clean(self):
        cleaned = super().clean()

        # Samakan dengan SIP Kendaraan: status tidak diubah dari form.
        # Edit hanya boleh saat Draft/Konsep atau Ditolak.
        if self.instance and self.instance.pk:
            status = getattr(self.instance, 'status', 'DRAFT')
            if status not in ['DRAFT', 'DITOLAK'] and not (self.user and self.user.is_superuser):
                raise ValidationError('SIP Rumah Negara hanya dapat diedit saat berstatus Draft/Konsep atau Ditolak.')

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'pejabat_penandatangan_pegawai' in self.fields:
            self.fields['pejabat_penandatangan_pegawai'].queryset = Pegawai.objects.select_related('unit_kerja').order_by('nama')
            self.fields['pejabat_penandatangan_pegawai'].required = False
            self.fields['pejabat_penandatangan_pegawai'].help_text = 'Pilih nama pejabat penandatangan dari Master Pegawai. Nama, NIP, dan jabatan akan digenerate pada PDF SIP Rumah Negara.'

        if 'jabatan_pejabat_penandatangan_display' in self.fields:
            pejabat = None
            if self.instance and getattr(self.instance, 'pejabat_penandatangan_pegawai_id', None):
                pejabat = self.instance.pejabat_penandatangan_pegawai
            jabatan = (getattr(pejabat, 'jabatan', '') or getattr(self.instance, 'jabatan_pejabat_penandatangan', '') or getattr(self.instance, 'pejabat_penandatangan', '') or '')
            self.fields['jabatan_pejabat_penandatangan_display'].initial = jabatan
            self.fields['jabatan_pejabat_penandatangan_display'].widget.attrs.update({
                'readonly': 'readonly',
                'aria-readonly': 'true',
            })

        if 'file_signed_pdf' in self.fields:
            self.fields['file_signed_pdf'].required = False
            self.fields['file_signed_pdf'].help_text = 'Opsional. Upload PDF SIP Rumah Negara yang sudah TTE. Jika diisi, status TTE otomatis menjadi Sudah TTE.'

        for field_name in ['tanggal_sip', 'tanggal_mulai', 'tanggal_akhir', 'tanggal_bayar_pnbp']:
            value = getattr(self.instance, field_name, None)

            if self.instance and self.instance.pk and value:
                self.fields[field_name].initial = value.strftime('%Y-%m-%d')

    def save(self, commit=True):
        instance = super().save(commit=False)
        pejabat = self.cleaned_data.get('pejabat_penandatangan_pegawai')
        if pejabat:
            instance.nama_pejabat_penandatangan = getattr(pejabat, 'nama', '') or ''
            instance.nip_pejabat_penandatangan = getattr(pejabat, 'nip', '') or ''
            instance.jabatan_pejabat_penandatangan = getattr(pejabat, 'jabatan', '') or ''
            instance.pejabat_penandatangan = instance.jabatan_pejabat_penandatangan or 'Pejabat Penandatangan'
        if self.cleaned_data.get('file_signed_pdf'):
            instance.dokumen_sip = self.cleaned_data.get('file_signed_pdf')
            instance.status_tte = 'SUDAH_TTE'
            instance.tanggal_tte = timezone.now()
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class SIPRumahCalonPenggunaTTEUploadForm(forms.ModelForm):
    class Meta:
        model = SIPRumahDinas
        fields = ['file_tte_calon_pengguna']
        labels = {
            'file_tte_calon_pengguna': 'Upload SIP Rumah Negara yang sudah TTE oleh Calon Pengguna Rumah',
        }
        widgets = {
            'file_tte_calon_pengguna': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,.pdf',
                'class': 'form-control'
            })
        }

    def clean_file_tte_calon_pengguna(self):
        dokumen = self.cleaned_data.get('file_tte_calon_pengguna')
        if not dokumen:
            raise ValidationError('File SIP Rumah Negara yang sudah TTE oleh calon pengguna rumah wajib diupload.')
        validate_pdf_file(dokumen)
        return dokumen


class SIPRumahSekjenTTEUploadForm(forms.ModelForm):
    class Meta:
        model = SIPRumahDinas
        fields = ['file_signed_pdf']
        labels = {
            'file_signed_pdf': 'Upload SIP Rumah Negara yang sudah TTE Sekjen/BSrE',
        }
        widgets = {
            'file_signed_pdf': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,.pdf',
                'class': 'form-control'
            })
        }

    def clean_file_signed_pdf(self):
        dokumen = self.cleaned_data.get('file_signed_pdf')
        if not dokumen:
            raise ValidationError('File SIP Rumah Negara yang sudah TTE Sekjen/BSrE wajib diupload.')
        validate_pdf_file(dokumen)
        return dokumen
