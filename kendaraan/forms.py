from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
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
    jenis_kendaraan_master = forms.CharField(
        label='Jenis Kendaraan (otomatis dari Master Kendaraan)',
        required=False,
        disabled=True,
    )
    kode_barang_master = forms.CharField(
        label='Kode Barang (otomatis dari Master Kendaraan)',
        required=False,
        disabled=True,
    )
    nup_master = forms.CharField(
        label='NUP (otomatis dari Master Kendaraan)',
        required=False,
        disabled=True,
    )
    class Meta:
        model = SIPKendaraan
        exclude = ['dibuat_oleh', 'pejabat_penandatangan', 'nama_pejabat_penerbit_sip_kendaraan', 'nip_pejabat_penerbit_sip_kendaraan', 'jabatan_pejabat_penerbit_sip_kendaraan', 'status_tte', 'tanggal_tte', 'catatan_tte', 'dokumen_sip', 'file_konsep_pdf', 'file_tte_pengusul', 'status_tte_pengusul', 'tanggal_tte_pengusul', 'catatan_tte_pengusul', 'file_final_pdf', 'tanggal_pengajuan', 'tanggal_persetujuan', 'disetujui_oleh', 'catatan_penolakan', 'status']

        labels = {
            'nomor_sip': 'Nomor SIP',
            'tanggal_sip': 'Tanggal SIP',
            'kendaraan': 'Kendaraan',
            'pegawai': 'Nama Pemegang SIP',
            'tanggal_mulai': 'Tanggal Mulai SIP',
            'tanggal_akhir': 'Tanggal Akhir / Masa Berlaku SIP',
            'masa_berlaku_sip': 'Keterangan Masa Berlaku SIP',
            'jenis_pemakaian': 'Jenis Kendaraan (snapshot sistem)',
            'tujuan_pemakaian': 'Tujuan Pemakaian',
            'lokasi_penggunaan': 'Lokasi Penggunaan',
            'dasar_penerbitan': 'Dasar Penerbitan',
            'pejabat_penerbit_sip_kendaraan': 'Pejabat Penandatangan SIP Kendaraan',
            'pejabat_penandatangan': 'Pejabat Penandatangan',
            'dokumen_sip': 'Dokumen SIP Kendaraan (PDF)',
            'dokumen_lainnya': 'Dokumen Lainnya / Lampiran Pendukung (Opsional)',
            'file_signed_pdf': 'Upload SIP Kendaraan yang sudah TTE',
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
            'file_signed_pdf': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,.pdf',
                'class': 'form-control'
            }),
        }


    def clean_file_signed_pdf(self):
        dokumen = self.cleaned_data.get('file_signed_pdf')
        if not dokumen:
            return dokumen
        validate_pdf_file(dokumen)
        return dokumen

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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Jenis kendaraan, kode barang, dan NUP tidak diinput manual pada SIP.
        # Data diambil otomatis dari Master Kendaraan berdasarkan kendaraan yang dipilih.
        if 'jenis_pemakaian' in self.fields:
            self.fields['jenis_pemakaian'].required = False
            self.fields['jenis_pemakaian'].widget = forms.HiddenInput()

        if 'pejabat_penerbit_sip_kendaraan' in self.fields:
            from master.models import Pegawai
            self.fields['pejabat_penerbit_sip_kendaraan'].label = 'Pejabat Penandatangan SIP Kendaraan'
            self.fields['pejabat_penerbit_sip_kendaraan'].queryset = Pegawai.objects.all().order_by('nama')
            self.fields['pejabat_penerbit_sip_kendaraan'].required = True
            self.fields['pejabat_penerbit_sip_kendaraan'].help_text = 'Pilih nama pegawai pejabat penandatangan SIP Kendaraan.'

        kendaraan_obj = getattr(self.instance, 'kendaraan', None)
        kendaraan_id = None
        if self.data:
            kendaraan_id = self.data.get('kendaraan')
        elif kendaraan_obj:
            kendaraan_id = getattr(kendaraan_obj, 'pk', None)

        if kendaraan_id and not kendaraan_obj:
            try:
                from master.models import Kendaraan
                kendaraan_obj = Kendaraan.objects.filter(pk=kendaraan_id).first()
            except Exception:
                kendaraan_obj = None

        if kendaraan_obj:
            self.fields['jenis_kendaraan_master'].initial = kendaraan_obj.get_jenis_kendaraan_display() if hasattr(kendaraan_obj, 'get_jenis_kendaraan_display') else (kendaraan_obj.jenis_kendaraan or '')
            self.fields['kode_barang_master'].initial = kendaraan_obj.kode_barang or ''
            self.fields['nup_master'].initial = kendaraan_obj.nup or ''
            if 'jenis_pemakaian' in self.fields:
                self.fields['jenis_pemakaian'].initial = kendaraan_obj.jenis_kendaraan or ''

        # Letakkan field otomatis tepat setelah pilihan kendaraan agar operator memahami sumber datanya.
        try:
            ordered = []
            for name in self.fields.keys():
                ordered.append(name)
                if name == 'kendaraan':
                    ordered.extend(['jenis_kendaraan_master', 'kode_barang_master', 'nup_master', 'pejabat_penerbit_sip_kendaraan'])
            seen = []
            for name in ordered:
                if name in self.fields and name not in seen:
                    seen.append(name)
            self.order_fields(seen)
        except Exception:
            pass

        # Supaya tanggal tetap tampil saat edit.
        for field_name in ['tanggal_sip', 'tanggal_mulai', 'tanggal_akhir']:
            value = getattr(self.instance, field_name, None)

            if self.instance and self.instance.pk and value:
                self.fields[field_name].initial = value.strftime('%Y-%m-%d')

    def save(self, commit=True):
        instance = super().save(commit=False)
        pejabat = self.cleaned_data.get('pejabat_penerbit_sip_kendaraan') if hasattr(self, 'cleaned_data') else None
        if pejabat:
            instance.pejabat_penerbit_sip_kendaraan = pejabat
            instance.nama_pejabat_penerbit_sip_kendaraan = getattr(pejabat, 'nama', '') or ''
            instance.nip_pejabat_penerbit_sip_kendaraan = getattr(pejabat, 'nip', '') or ''
            instance.jabatan_pejabat_penerbit_sip_kendaraan = getattr(pejabat, 'jabatan', '') or 'Pejabat Penerbit SIP Kendaraan'
            instance.pejabat_penandatangan = instance.jabatan_pejabat_penerbit_sip_kendaraan
        uploaded_tte = self.cleaned_data.get('file_signed_pdf') if hasattr(self, 'cleaned_data') else None
        if uploaded_tte:
            # File ini adalah hasil SIP yang sudah TTE; simpan juga sebagai dokumen_sip
            # agar preview lama dan detail SIP menampilkan dokumen final.
            instance.dokumen_sip = uploaded_tte
            instance.status_tte = 'SUDAH_TTE'
            instance.tanggal_tte = timezone.now()
            instance.catatan_tte = 'SIP Kendaraan yang sudah TTE diupload melalui Form SIP Kendaraan.'
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def clean(self):
        cleaned = super().clean()

        # Pengelola BMN hanya boleh menyusun Draft/Konsep.
        # Perubahan status dilakukan melalui tombol Ajukan/Setujui/Tolak,
        # bukan dari form input biasa.
        if self.instance and self.instance.pk:
            status = getattr(self.instance, 'status', 'DRAFT')
            if status not in ['DRAFT', 'DITOLAK', 'DIAJUKAN'] and not (self.user and self.user.is_superuser):
                raise ValidationError('SIP Kendaraan hanya dapat diedit saat berstatus Draft/Konsep, Diajukan, atau Ditolak.')

        kendaraan = cleaned.get('kendaraan')
        if kendaraan:
            # Snapshot jenis kendaraan otomatis mengikuti Master Kendaraan.
            cleaned['jenis_pemakaian'] = kendaraan.jenis_kendaraan

        pejabat = cleaned.get('pejabat_penerbit_sip_kendaraan')
        if pejabat:
            self.instance.pejabat_penerbit_sip_kendaraan = pejabat
            self.instance.nama_pejabat_penerbit_sip_kendaraan = getattr(pejabat, 'nama', '') or ''
            self.instance.nip_pejabat_penerbit_sip_kendaraan = getattr(pejabat, 'nip', '') or ''
            self.instance.jabatan_pejabat_penerbit_sip_kendaraan = getattr(pejabat, 'jabatan', '') or 'Pejabat Penerbit SIP Kendaraan'
            self.instance.pejabat_penandatangan = self.instance.jabatan_pejabat_penerbit_sip_kendaraan
        return cleaned


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
            'file_signed_pdf': 'Upload SIP Kendaraan yang sudah TTE',
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
            raise ValidationError('File SIP Kendaraan yang sudah TTE wajib diupload.')
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
            if status not in ['DRAFT', 'DITOLAK', 'DIAJUKAN'] and not (self.user and self.user.is_superuser):
                raise ValidationError('SIP Kendaraan hanya dapat diedit saat berstatus Draft/Konsep, Diajukan, atau Ditolak.')

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
            if status not in ['DRAFT', 'DITOLAK', 'DIAJUKAN'] and not (self.user and self.user.is_superuser):
                raise ValidationError('SIP Kendaraan hanya dapat diedit saat berstatus Draft/Konsep, Diajukan, atau Ditolak.')

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.tanggal:
            self.fields['tanggal'].initial = self.instance.tanggal.strftime('%Y-%m-%d')