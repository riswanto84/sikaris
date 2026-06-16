from django import forms
from django.utils import timezone

from core.access import is_biro_umum_user, is_global_bmn_scope_user, get_user_unit_kerja, get_accessible_unit_ids_for_user
from master.models import Kendaraan, Pegawai, RumahDinas, UnitKerja
from tanah_negara.models import TanahNegara
from .models import PermohonanPenghapusanBMN


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


class PermohonanPenghapusanBMNForm(forms.ModelForm):
    foto_kondisi_files = MultipleImageField(required=False, label='Foto Kondisi Aset', widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*,.jpg,.jpeg,.png', 'class': 'form-control'}), help_text='Bisa upload lebih dari satu foto kondisi aset.')
    class Meta:
        model = PermohonanPenghapusanBMN
        fields = [
            'tanggal_permohonan', 'unit_kerja', 'pemohon',
            'nup', 'nama_barang', 'nilai_perolehan',
            'kondisi_barang', 'lokasi_barang', 'alasan_penghapusan',
            'uraian_alasan', 'dasar_usulan', 'dokumen_usulan',
            'dokumen_pendukung', 'foto_kondisi_files', 'status', 'catatan_unit',
            'catatan_biro_umum', 'nomor_persetujuan', 'tanggal_persetujuan',
            'dokumen_persetujuan', 'nomor_sk_penghapusan',
            'tanggal_sk_penghapusan', 'dokumen_sk_penghapusan',
            'berita_acara_penghapusan',
            'status_tte', 'pejabat_tte', 'nip_pejabat_tte', 'tanggal_tte',
            'file_sebelum_tte', 'file_setelah_tte', 'catatan_tte',
        ]
        labels = {
            'tanggal_permohonan': 'Tanggal Permohonan',
            'unit_kerja': 'Unit Kerja/Satker Pemohon',
            'pemohon': 'Pegawai Pemohon/PIC Unit Kerja',
            'nup': 'NUP',
            'nama_barang': 'Nama Barang/Aset',
            'nilai_perolehan': 'Nilai Perolehan',
            'kondisi_barang': 'Kondisi Barang',
            'lokasi_barang': 'Lokasi Barang',
            'alasan_penghapusan': 'Alasan Penghapusan',
            'dokumen_usulan': 'Dokumen Usulan Unit Kerja',
            'dokumen_pendukung': 'Dokumen Pendukung',
            'foto_kondisi_files': 'Foto Kondisi Aset',
            'catatan_unit': 'Catatan Unit Kerja',
            'catatan_biro_umum': 'Catatan Biro Umum',
            'nomor_persetujuan': 'Nomor Persetujuan/Penetapan',
            'tanggal_persetujuan': 'Tanggal Persetujuan/Penetapan',
            'dokumen_persetujuan': 'Dokumen Persetujuan/Penetapan',
            'nomor_sk_penghapusan': 'Nomor SK Penghapusan',
            'tanggal_sk_penghapusan': 'Tanggal SK Penghapusan',
            'dokumen_sk_penghapusan': 'Dokumen SK Penghapusan',
            'berita_acara_penghapusan': 'Berita Acara Penghapusan/Pemusnahan/Pemindahtanganan',
            'status_tte': 'Status TTE BSrE',
            'pejabat_tte': 'Pejabat TTE BSrE',
            'nip_pejabat_tte': 'NIP Pejabat TTE BSrE',
            'tanggal_tte': 'Tanggal/Waktu TTE BSrE',
            'file_sebelum_tte': 'File Sebelum TTE BSrE (PDF)',
            'file_setelah_tte': 'File Setelah TTE BSrE (PDF)',
            'catatan_tte': 'Catatan TTE',
        }
        widgets = {
            'tanggal_permohonan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_persetujuan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_sk_penghapusan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_tte': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
            'uraian_alasan': forms.Textarea(attrs={'rows': 4}),
            'dasar_usulan': forms.Textarea(attrs={'rows': 3}),
            'lokasi_barang': forms.Textarea(attrs={'rows': 2}),
            'catatan_unit': forms.Textarea(attrs={'rows': 3}),
            'catatan_biro_umum': forms.Textarea(attrs={'rows': 3}),
            'dokumen_usulan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,.pdf'}),
            'dokumen_pendukung': forms.ClearableFileInput(attrs={'accept': 'application/pdf,.pdf'}),
            'dokumen_persetujuan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            'dokumen_sk_penghapusan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            'berita_acara_penghapusan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            'file_sebelum_tte': forms.ClearableFileInput(attrs={'accept': 'application/pdf,.pdf'}),
            'file_setelah_tte': forms.ClearableFileInput(attrs={'accept': 'application/pdf,.pdf'}),
            'catatan_tte': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})

        self.fields['unit_kerja'].queryset = UnitKerja.objects.order_by('nama_unit')
        self.fields['pemohon'].queryset = Pegawai.objects.select_related('unit_kerja').order_by('nama')

        if self.user and not is_global_bmn_scope_user(self.user):
            unit = get_user_unit_kerja(self.user)
            unit_ids = get_accessible_unit_ids_for_user(self.user) or []
            if unit_ids:
                self.fields['unit_kerja'].queryset = UnitKerja.objects.filter(pk__in=unit_ids).order_by('nama_unit')
                if unit:
                    self.fields['unit_kerja'].initial = unit.pk
                self.fields['pemohon'].queryset = Pegawai.objects.filter(unit_kerja_id__in=unit_ids).order_by('nama')

            # Unit kerja hanya mengajukan/memperbaiki usulan, tidak mengisi bagian keputusan Biro Umum.
            biro_only_fields = [
                'status', 'catatan_biro_umum', 'nomor_persetujuan', 'tanggal_persetujuan',
                'dokumen_persetujuan', 'nomor_sk_penghapusan', 'tanggal_sk_penghapusan',
                'dokumen_sk_penghapusan', 'berita_acara_penghapusan',
                'status_tte', 'pejabat_tte', 'nip_pejabat_tte', 'tanggal_tte',
                'file_sebelum_tte', 'file_setelah_tte', 'catatan_tte',
            ]
            for field in biro_only_fields:
                self.fields.pop(field, None)
        else:
            self.fields['status'].help_text = 'Status ini dikelola Biro Umum setelah permohonan diajukan unit kerja.'

        if self.instance and self.instance.pk:
            for date_field in ['tanggal_permohonan', 'tanggal_persetujuan', 'tanggal_sk_penghapusan']:
                value = getattr(self.instance, date_field, None)
                if value and date_field in self.fields:
                    self.fields[date_field].initial = value.strftime('%Y-%m-%d')
            for dt_field in ['tanggal_tte']:
                value = getattr(self.instance, dt_field, None)
                if value and dt_field in self.fields:
                    self.fields[dt_field].initial = value.strftime('%Y-%m-%dT%H:%M')

    def clean_dokumen_usulan(self):
        return validate_pdf(self.cleaned_data.get('dokumen_usulan'), 'Dokumen usulan unit kerja')

    def clean_dokumen_pendukung(self):
        return validate_pdf(self.cleaned_data.get('dokumen_pendukung'), 'Dokumen pendukung')

    def clean_file_sebelum_tte(self):
        return validate_pdf(self.cleaned_data.get('file_sebelum_tte'), 'File sebelum TTE BSrE')

    def clean_file_setelah_tte(self):
        return validate_pdf(self.cleaned_data.get('file_setelah_tte'), 'File setelah TTE BSrE')

    def clean(self):
        cleaned = super().clean()
        # Field jenis aset/kendaraan/rumah/tanah/kode barang tidak ditampilkan lagi pada form.
        # Detail barang banyak dicatat melalui import Excel, sedangkan ringkasan usulan cukup memakai nama barang/NUP/nilai.
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not getattr(obj, 'jenis_aset', None):
            obj.jenis_aset = 'LAINNYA'
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class ImportBarangPenghapusanForm(forms.Form):
    file_excel = forms.FileField(
        label='File Excel Barang yang Akan Dihapus',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'class': 'form-control'}),
        help_text='Gunakan template Excel yang tersedia. Kolom: no, kode_barang, nup, nama_barang, jenis_aset, kuantitas, nilai_perolehan, kondisi_barang, lokasi_barang, alasan_penghapusan, keterangan.'
    )
    replace_existing = forms.BooleanField(
        required=False,
        initial=True,
        label='Ganti detail barang lama dengan isi file ini',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
