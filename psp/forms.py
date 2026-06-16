from django import forms

from core.access import get_user_unit_kerja, is_global_bmn_scope_user, get_accessible_unit_ids_for_user
from core.roles import is_sekretaris_jenderal
from master.models import Pegawai, UnitKerja
from .models import PermohonanPSPBMN

PDF_ACCEPT = 'application/pdf,.pdf'
EXCEL_ACCEPT = '.xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


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
            'tanggal_permohonan', 'unit_kerja', 'pemohon',
            'judul_paket', 'nomor_tiket_siman', 'kode_satuan_kerja', 'nama_satuan_kerja',
            'jenis_barang', 'batas_nilai_per_unit', 'nilai_psp', 'keterangan_barang',
            'dokumen_permohonan_psp',
            'foto_barang_files', 'dokumen_kepemilikan', 'surat_pernyataan_pengganti_kepemilikan',
            'status', 'catatan_unit', 'catatan_biro_umum', 'catatan_biro_hukum',
            'nomor_nota_permohonan_psp', 'tanggal_nota_permohonan_psp',
            'nomor_surat_keterangan_digital', 'tanggal_surat_keterangan_digital',
            'nomor_surat_pernyataan_formil_materiil', 'tanggal_surat_pernyataan_formil_materiil',
            'nomor_nota_biro_hukum', 'tanggal_nota_biro_hukum',
            'nomor_sk_psp', 'tanggal_sk_psp', 'sk_penetapan_psp',
            'status_tte', 'pejabat_tte', 'nip_pejabat_tte', 'tanggal_tte', 'file_sebelum_tte',
            'status_emeterai', 'nomor_serial_emeterai', 'tanggal_emeterai', 'dokumen_bermeterai',
        ]
        labels = {
            'tanggal_permohonan': 'Tanggal Permohonan',
            'unit_kerja': 'Unit Kerja/Satker Pemohon',
            'pemohon': 'Pegawai Pemohon/PIC Unit Kerja',
            'judul_paket': 'Judul Paket PSP Banyak Barang',
            'nomor_tiket_siman': 'Nomor Tiket SIMAN V2',
            'kode_satuan_kerja': 'Kode Satuan Kerja',
            'nama_satuan_kerja': 'Nama Satuan Kerja',
            'jenis_barang': 'Jenis Barang/Aset BMN',
            'batas_nilai_per_unit': 'Batas Nilai Per Unit',
            'nilai_psp': 'Nilai PSP / Total Nilai Perolehan',
            'keterangan_barang': 'Keterangan Barang',
            'dokumen_permohonan_psp': 'Dokumen PSP SIKARIS Final/Gabungan (PDF)',
            'foto_barang_files': 'Foto Barang',
            'dokumen_kepemilikan': 'Dokumen Kepemilikan Kendaraan (PDF)',
            'surat_pernyataan_pengganti_kepemilikan': 'Surat Pernyataan Pengganti Dokumen Kepemilikan (PDF)',
            'status': 'Status Permohonan',
            'catatan_unit': 'Catatan Unit Kerja',
            'catatan_biro_umum': 'Catatan Biro Umum',
            'catatan_biro_hukum': 'Catatan Biro Hukum',
            'nomor_nota_permohonan_psp': 'Nomor Nota Permohonan ke Sekjen',
            'tanggal_nota_permohonan_psp': 'Tanggal Nota Permohonan ke Sekjen',
            'nomor_surat_keterangan_digital': 'Nomor Surat Keterangan Dokumen Digital',
            'nomor_surat_pernyataan_formil_materiil': 'Nomor Surat Pernyataan Formil dan Materiil',
            'nomor_nota_biro_hukum': 'Nomor Nota ke Biro Hukum',
            'tanggal_nota_biro_hukum': 'Tanggal Nota ke Biro Hukum',
            'nomor_sk_psp': 'Nomor SK PSP',
            'tanggal_sk_psp': 'Tanggal SK PSP',
            'sk_penetapan_psp': 'SK Penetapan PSP Final (PDF TTE BSrE)',
            'status_tte': 'Status TTE BSrE',
            'pejabat_tte': 'Pejabat TTE BSrE',
            'nip_pejabat_tte': 'NIP Pejabat TTE BSrE',
            'tanggal_tte': 'Tanggal/Waktu TTE BSrE',
            'file_sebelum_tte': 'File Sebelum TTE BSrE (PDF)',
            'status_emeterai': 'Status e-Meterai',
            'nomor_serial_emeterai': 'Nomor Serial e-Meterai',
            'tanggal_emeterai': 'Tanggal/Waktu e-Meterai',
            'dokumen_bermeterai': 'Dokumen Bermeterai Elektronik (PDF)',
        }
        help_texts = {
            'nomor_tiket_siman': 'Contoh: PP126010610424145813. Nomor ini akan muncul pada monitoring PSP dan dokumen pengantar.',
            'nilai_psp': 'Jika memakai lampiran barang banyak, nilai ini akan otomatis direkap dari detail barang setelah import Excel.',
            'batas_nilai_per_unit': 'Default Rp100.000.000. Sistem memberi penanda bila ada barang melebihi batas.',
            'dokumen_permohonan_psp': 'Upload PDF Dokumen PSP SIKARIS yang sudah ditandatangani. Bisa TTE BSrE atau tanda tangan manual, dan bisa memakai meterai biasa/e-Meterai sesuai kebutuhan. Wajib diunggah sebelum Biro Umum meneruskan PSP ke Sekjen.',
            'nomor_nota_permohonan_psp': 'Nomor pada dokumen Word hasil generate dapat diedit manual sebelum PDF final diupload.',
            'nomor_sk_psp': 'Boleh dikosongkan saat status SK Terbit/Selesai. Sistem otomatis membuat format nomor/HUK/tahun.',
            'file_sebelum_tte': 'PDF final bersih yang akan dikirim ke layanan TTE BSrE.',
            'dokumen_bermeterai': 'Untuk surat pernyataan bermeterai, unggah PDF yang sudah dibubuhi e-Meterai resmi. e-Meterai dan TTE sebaiknya berdampingan, tidak saling menimpa.',
        }
        widgets = {
            'tanggal_permohonan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_nota_permohonan_psp': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_surat_keterangan_digital': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_surat_pernyataan_formil_materiil': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_nota_biro_hukum': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_sk_psp': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_tte': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
            'tanggal_emeterai': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
            'keterangan_barang': forms.Textarea(attrs={'rows': 3}),
            'catatan_unit': forms.Textarea(attrs={'rows': 3}),
            'catatan_biro_umum': forms.Textarea(attrs={'rows': 3}),
            'catatan_biro_hukum': forms.Textarea(attrs={'rows': 3}),
            'dokumen_permohonan_psp': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
            'dokumen_kepemilikan': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
            'surat_pernyataan_pengganti_kepemilikan': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
            'sk_penetapan_psp': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
            'file_sebelum_tte': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
            'dokumen_bermeterai': forms.ClearableFileInput(attrs={'accept': PDF_ACCEPT}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Lima dokumen persyaratan ini tidak lagi ditampilkan pada Form Permohonan PSP BMN.
        # Jika diperlukan, pemohon dapat memakai Dokumen Permohonan PSP Gabungan (PDF)
        # atau Import Barang/Lampiran pendukung sesuai alur PSP terbaru.
        hidden_requirement_fields = [
            'surat_permohonan_satker',
            'surat_pengantar_eselon1',
            'daftar_kondisi_barang',
            'laporan_sub_kelompok_barang',
            'surat_pernyataan_kepala_satker',
        ]
        for field_name in hidden_requirement_fields:
            self.fields.pop(field_name, None)

        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})

        self.fields['unit_kerja'].queryset = UnitKerja.objects.order_by('nama_unit')
        self.fields['pemohon'].queryset = Pegawai.objects.select_related('unit_kerja').order_by('nama')

        if self.user and not (is_global_bmn_scope_user(self.user) or is_sekretaris_jenderal(self.user)):
            unit = get_user_unit_kerja(self.user)
            unit_ids = get_accessible_unit_ids_for_user(self.user) or []
            if unit_ids:
                self.fields['unit_kerja'].queryset = UnitKerja.objects.filter(pk__in=unit_ids).order_by('nama_unit')
                if unit:
                    self.fields['unit_kerja'].initial = unit.pk
                self.fields['pemohon'].queryset = Pegawai.objects.filter(unit_kerja_id__in=unit_ids).order_by('nama')
            biro_only_fields = [
                'status', 'catatan_biro_umum', 'catatan_biro_hukum',
                'nomor_nota_permohonan_psp', 'tanggal_nota_permohonan_psp',
                'nomor_surat_keterangan_digital', 'tanggal_surat_keterangan_digital',
                'nomor_surat_pernyataan_formil_materiil', 'tanggal_surat_pernyataan_formil_materiil',
                'nomor_nota_biro_hukum', 'tanggal_nota_biro_hukum',
                'nomor_sk_psp', 'tanggal_sk_psp', 'sk_penetapan_psp',
                'status_tte', 'pejabat_tte', 'nip_pejabat_tte', 'tanggal_tte', 'file_sebelum_tte', 'file_setelah_tte',
                'status_emeterai', 'nomor_serial_emeterai', 'tanggal_emeterai', 'dokumen_bermeterai',
            ]
            for field in biro_only_fields:
                self.fields.pop(field, None)
        else:
            for field in ['nomor_nota_permohonan_psp', 'nomor_surat_keterangan_digital', 'nomor_surat_pernyataan_formil_materiil', 'nomor_nota_biro_hukum', 'nomor_sk_psp']:
                if field in self.fields:
                    self.fields[field].required = False
                    self.fields[field].widget.attrs['placeholder'] = 'Kosongkan agar dibuat otomatis oleh sistem'

        if self.instance and self.instance.pk:
            for date_field in [
                'tanggal_permohonan', 'tanggal_nota_permohonan_psp', 'tanggal_surat_keterangan_digital',
                'tanggal_surat_pernyataan_formil_materiil', 'tanggal_nota_biro_hukum', 'tanggal_sk_psp'
            ]:
                value = getattr(self.instance, date_field, None)
                if value and date_field in self.fields:
                    self.fields[date_field].initial = value.strftime('%Y-%m-%d')
            for dt_field in ['tanggal_tte', 'tanggal_emeterai']:
                value = getattr(self.instance, dt_field, None)
                if value and dt_field in self.fields:
                    self.fields[dt_field].initial = value.strftime('%Y-%m-%dT%H:%M')

        for dt_field in ['tanggal_tte', 'tanggal_emeterai']:
            if dt_field in self.fields:
                self.fields[dt_field].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']

    def _has_file(self, field_name):
        new_file = self.cleaned_data.get(field_name)
        old_file = getattr(self.instance, field_name, None)
        return bool(new_file or old_file)

    def clean_dokumen_permohonan_psp(self):
        return validate_pdf(self.cleaned_data.get('dokumen_permohonan_psp'), 'Dokumen permohonan PSP gabungan')

    def clean_surat_permohonan_satker(self):
        return validate_pdf(self.cleaned_data.get('surat_permohonan_satker'), 'Surat Permohonan Satker')

    def clean_surat_pengantar_eselon1(self):
        return validate_pdf(self.cleaned_data.get('surat_pengantar_eselon1'), 'Surat Pengantar Eselon I')

    def clean_daftar_kondisi_barang(self):
        return validate_pdf(self.cleaned_data.get('daftar_kondisi_barang'), 'Daftar Kondisi Barang')

    def clean_laporan_sub_kelompok_barang(self):
        return validate_pdf(self.cleaned_data.get('laporan_sub_kelompok_barang'), 'Laporan Sub-Sub Kelompok Barang')

    def clean_surat_pernyataan_kepala_satker(self):
        return validate_pdf(self.cleaned_data.get('surat_pernyataan_kepala_satker'), 'Surat Pernyataan Kepala Satker')

    def clean_dokumen_kepemilikan(self):
        return validate_pdf(self.cleaned_data.get('dokumen_kepemilikan'), 'Dokumen kepemilikan')

    def clean_surat_pernyataan_pengganti_kepemilikan(self):
        return validate_pdf(self.cleaned_data.get('surat_pernyataan_pengganti_kepemilikan'), 'Surat pernyataan pengganti dokumen kepemilikan')

    def clean_sk_penetapan_psp(self):
        return validate_pdf(self.cleaned_data.get('sk_penetapan_psp'), 'SK Penetapan PSP')

    def clean_file_sebelum_tte(self):
        return validate_pdf(self.cleaned_data.get('file_sebelum_tte'), 'File sebelum TTE BSrE')

    def clean_dokumen_bermeterai(self):
        return validate_pdf(self.cleaned_data.get('dokumen_bermeterai'), 'Dokumen bermeterai elektronik')

    def clean(self):
        cleaned = super().clean()
        jenis = cleaned.get('jenis_barang')
        nilai = cleaned.get('nilai_psp') or 0
        status_tte = cleaned.get('status_tte')
        status_emeterai = cleaned.get('status_emeterai')

        # Dokumen PSP SIKARIS Final/Gabungan tidak wajib saat membuat draft/usulan awal.
        # Validasi wajib dilakukan saat Biro Umum meneruskan usulan PSP ke Sekjen.

        foto_files = cleaned.get('foto_barang_files') or []
        has_existing_photos = bool(self.instance and self.instance.pk and self.instance.foto_barang_list.exists())
        if jenis == 'KENDARAAN' and nilai and nilai > 100000000:
            if not foto_files and not has_existing_photos:
                self.add_error('foto_barang_files', 'Foto barang wajib diunggah untuk kendaraan dengan nilai PSP di atas Rp100 juta.')
            if not self._has_file('dokumen_kepemilikan') and not self._has_file('surat_pernyataan_pengganti_kepemilikan'):
                raise forms.ValidationError('Untuk kendaraan dengan nilai PSP di atas Rp100 juta, unggah dokumen kepemilikan kendaraan atau surat pernyataan pengganti dokumen kepemilikan jika dokumen kepemilikan tidak tersedia.')

        if status_tte == 'SUDAH_TTE' and not self._has_file('file_setelah_tte') and not self._has_file('sk_penetapan_psp'):
            self.add_error('file_setelah_tte', 'Jika status sudah TTE BSrE, unggah file hasil TTE BSrE atau SK Penetapan PSP final.')
        if status_emeterai == 'SUDAH' and not self._has_file('dokumen_bermeterai'):
            self.add_error('dokumen_bermeterai', 'Jika status sudah e-Meterai, unggah dokumen PDF yang telah dibubuhi e-Meterai.')
        return cleaned


class ImportBarangPSPForm(forms.Form):
    file_excel = forms.FileField(
        label='File Excel Lampiran Barang PSP',
        widget=forms.ClearableFileInput(attrs={'accept': EXCEL_ACCEPT, 'class': 'form-control'}),
        help_text='Format .xlsx. Kolom: no, kode_satuan_kerja, nama_satuan_kerja, kode_barang, nup, nama_barang, tipe_barang, tahun_perolehan, kuantitas, nilai_perolehan, kondisi_barang, keterangan.'
    )
    replace_existing = forms.BooleanField(
        label='Hapus detail barang lama sebelum import',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_file_excel(self):
        f = self.cleaned_data.get('file_excel')
        if f and not f.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('File import harus berformat .xlsx')
        return f
