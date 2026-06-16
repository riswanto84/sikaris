from django import forms
from django.core.exceptions import ValidationError
from core.access import filter_form_fields_by_user

from .models import (
    SIPKendaraan,
    ServiceKendaraan,
    RiwayatKondisiKendaraan,
)


# ============================================================
# VALIDATOR FILE
# ============================================================

def validate_pdf_file(uploaded_file):
    """
    Validator khusus untuk dokumen SIP kendaraan.
    Hanya menerima PDF.
    """
    if not uploaded_file:
        return

    filename = uploaded_file.name.lower()

    if not filename.endswith('.pdf'):
        raise ValidationError('Dokumen SIP kendaraan hanya boleh berupa file PDF.')

    content_type = getattr(uploaded_file, 'content_type', '')

    if content_type and content_type not in ['application/pdf', 'application/x-pdf']:
        raise ValidationError('Format file tidak valid. Upload dokumen dalam format PDF.')


def validate_dokumen_lainnya_file(uploaded_file):
    """
    Validator lampiran pendukung opsional.
    Menerima PDF, gambar, Word, dan Excel agar dapat mengakomodir dokumen lampiran.
    """
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


def validate_kuitansi_file(uploaded_file):
    """
    Validator untuk bukti kuitansi service.
    Menerima gambar dan PDF.
    """
    if not uploaded_file:
        return

    filename = uploaded_file.name.lower()

    allowed_extensions = (
        '.jpg',
        '.jpeg',
        '.png',
        '.webp',
        '.pdf',
    )

    if not filename.endswith(allowed_extensions):
        raise ValidationError(
            'Bukti kuitansi hanya boleh berupa file JPG, JPEG, PNG, WEBP, atau PDF.'
        )


# ============================================================
# MULTIPLE FILE UPLOAD
# ============================================================

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]

        return single_file_clean(data, initial)


# ============================================================
# BASE FORM
# ============================================================

class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user is not None:
            filter_form_fields_by_user(self, self.user)

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


# ============================================================
# FORM SIP KENDARAAN
# ============================================================

class SIPKendaraanForm(BootstrapModelForm):
    class Meta:
        model = SIPKendaraan
        exclude = ['dibuat_oleh', 'pejabat_penandatangan', 'pejabat_penerbit_sip_kendaraan', 'nama_pejabat_penerbit_sip_kendaraan', 'nip_pejabat_penerbit_sip_kendaraan', 'jabatan_pejabat_penerbit_sip_kendaraan', 'status_tte', 'tanggal_tte', 'catatan_tte', 'dokumen_sip', 'file_konsep_pdf', 'file_tte_pengusul', 'status_tte_pengusul', 'tanggal_tte_pengusul', 'catatan_tte_pengusul', 'file_final_pdf', 'file_signed_pdf', 'tanggal_pengajuan', 'tanggal_persetujuan', 'disetujui_oleh', 'catatan_penolakan', 'status']

        labels = {
            'nomor_sip': 'Nomor SIP',
            'tanggal_sip': 'Tanggal SIP',
            'kendaraan': 'Kendaraan',
            'pegawai': 'Pegawai',
            'tanggal_mulai': 'Tanggal Mulai SIP',
            'tanggal_akhir': 'Tanggal Akhir / Masa Berlaku SIP',
            'masa_berlaku_sip': 'Keterangan Masa Berlaku SIP',
            'jenis_pemakaian': 'Jenis Kendaraan',
            'tujuan_pemakaian': 'Tujuan Pemakaian',
            'lokasi_penggunaan': 'Lokasi Penggunaan',
            'dasar_penerbitan': 'Dasar Penerbitan',
            'pejabat_penandatangan': 'Pejabat Penandatangan',
            'dokumen_sip': 'Dokumen SIP Kendaraan (PDF)',
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
            'dokumen_sip': forms.ClearableFileInput(attrs={
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

        # Kalau edit data dan tidak upload file baru,
        # dokumen lama tetap dipakai.
        if not dokumen:
            return dokumen

        validate_pdf_file(dokumen)
        return dokumen


    def clean(self):
        cleaned = super().clean()

        # Pengelola BMN hanya boleh menyusun Draft/Konsep.
        # Perubahan status dilakukan melalui tombol Ajukan/Setujui/Tolak,
        # bukan dari form input biasa.
        if self.instance and self.instance.pk:
            status = getattr(self.instance, 'status', 'DRAFT')
            if status not in ['DRAFT', 'DITOLAK'] and not (self.user and self.user.is_superuser):
                raise ValidationError('SIP Kendaraan hanya dapat diedit saat berstatus Draft/Konsep atau Ditolak.')

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Supaya tanggal tetap tampil saat edit.
        for field_name in ['tanggal_sip', 'tanggal_mulai', 'tanggal_akhir']:
            value = getattr(self.instance, field_name, None)

            if self.instance and self.instance.pk and value:
                self.fields[field_name].initial = value.strftime('%Y-%m-%d')




class SIPKendaraanPengusulTTEUploadForm(forms.ModelForm):
    class Meta:
        model = SIPKendaraan
        fields = ['file_tte_pengusul']
        labels = {
            'file_tte_pengusul': 'Upload SIP Kendaraan yang sudah TTE oleh Pegawai Pengusul',
        }
        widgets = {
            'file_tte_pengusul': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,.pdf',
                'class': 'form-control'
            })
        }

    def clean_file_tte_pengusul(self):
        dokumen = self.cleaned_data.get('file_tte_pengusul')
        if not dokumen:
            raise ValidationError('File SIP Kendaraan yang sudah TTE oleh pegawai pengusul wajib diupload.')
        validate_pdf_file(dokumen)
        return dokumen


class SIPKendaraanBSREUploadForm(forms.ModelForm):
    class Meta:
        model = SIPKendaraan
        fields = ['file_signed_pdf']
        labels = {
            'file_signed_pdf': 'Upload SIP Kendaraan yang sudah TTE BSrE',
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
            raise ValidationError('File SIP Kendaraan yang sudah TTE BSrE wajib diupload.')
        validate_pdf_file(dokumen)
        return dokumen


# ============================================================
# FORM SERVICE KENDARAAN
# ============================================================

class ServiceKendaraanForm(BootstrapModelForm):
    kuitansi_files = MultipleFileField(
        required=False,
        label='Upload Bukti Kuitansi',
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': 'image/*,.pdf',
            'class': 'form-control'
        }),
        help_text='Bisa upload lebih dari satu file kuitansi. Format: JPG, JPEG, PNG, WEBP, atau PDF.'
    )

    class Meta:
        model = ServiceKendaraan

        # Field lama disembunyikan dari form.
        # Data lama tetap aman di database.
        exclude = [
            'dicatat_oleh',
            'dokumen_bukti',
            'foto_sebelum',
            'foto_sesudah',
            'total_biaya',
        ]

        labels = {
            'kendaraan': 'Kendaraan',
            'tanggal_service': 'Tanggal Service',
            'jenis_service': 'Jenis Service',
            'kilometer': 'Kilometer',
            'bengkel': 'Bengkel',
            'uraian_pekerjaan': 'Uraian Pekerjaan',
            'sparepart_diganti': 'Sparepart Diganti',
            'biaya_jasa': 'Biaya Jasa',
            'biaya_sparepart': 'Biaya Sparepart',
            'kondisi_sebelum': 'Kondisi Sebelum',
            'kondisi_sesudah': 'Kondisi Sesudah',
        }

        widgets = {
            'tanggal_service': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
        }

    def clean_kuitansi_files(self):
        files = self.cleaned_data.get('kuitansi_files')

        if not files:
            return files

        if not isinstance(files, list):
            files = [files]

        for uploaded_file in files:
            validate_kuitansi_file(uploaded_file)

        return files


    def clean(self):
        cleaned = super().clean()

        # Pengelola BMN hanya boleh menyusun Draft/Konsep.
        # Perubahan status dilakukan melalui tombol Ajukan/Setujui/Tolak,
        # bukan dari form input biasa.
        if self.instance and self.instance.pk:
            status = getattr(self.instance, 'status', 'DRAFT')
            if status not in ['DRAFT', 'DITOLAK'] and not (self.user and self.user.is_superuser):
                raise ValidationError('SIP Kendaraan hanya dapat diedit saat berstatus Draft/Konsep atau Ditolak.')

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Supaya tanggal service tetap tampil saat edit.
        if self.instance and self.instance.pk and self.instance.tanggal_service:
            self.fields['tanggal_service'].initial = self.instance.tanggal_service.strftime('%Y-%m-%d')


# ============================================================
# FORM RIWAYAT KONDISI KENDARAAN
# ============================================================

class RiwayatKondisiKendaraanForm(BootstrapModelForm):
    class Meta:
        model = RiwayatKondisiKendaraan
        exclude = ['dicatat_oleh']

        labels = {
            'kendaraan': 'Kendaraan',
            'tanggal': 'Tanggal',
            'kondisi': 'Kondisi',
            'uraian_kondisi': 'Uraian Kondisi',
            'foto_kondisi': 'Foto Kondisi',
        }

        widgets = {
            'tanggal': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
        }


    def clean(self):
        cleaned = super().clean()

        # Pengelola BMN hanya boleh menyusun Draft/Konsep.
        # Perubahan status dilakukan melalui tombol Ajukan/Setujui/Tolak,
        # bukan dari form input biasa.
        if self.instance and self.instance.pk:
            status = getattr(self.instance, 'status', 'DRAFT')
            if status not in ['DRAFT', 'DITOLAK'] and not (self.user and self.user.is_superuser):
                raise ValidationError('SIP Kendaraan hanya dapat diedit saat berstatus Draft/Konsep atau Ditolak.')

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.tanggal:
            self.fields['tanggal'].initial = self.instance.tanggal.strftime('%Y-%m-%d')