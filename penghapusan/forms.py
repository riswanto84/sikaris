from django import forms
from django.utils import timezone

from core.access import is_biro_umum_user, get_user_unit_kerja
from master.models import Kendaraan, Pegawai, RumahDinas, UnitKerja
from tanah_negara.models import TanahNegara
from .models import PermohonanPenghapusanBMN


class PermohonanPenghapusanBMNForm(forms.ModelForm):
    class Meta:
        model = PermohonanPenghapusanBMN
        fields = [
            'tanggal_permohonan', 'unit_kerja', 'pemohon', 'jenis_aset',
            'kendaraan', 'rumah_negara', 'tanah_negara',
            'kode_barang', 'nup', 'nama_barang', 'nilai_perolehan',
            'kondisi_barang', 'lokasi_barang', 'alasan_penghapusan',
            'uraian_alasan', 'dasar_usulan', 'dokumen_usulan',
            'dokumen_pendukung', 'foto_kondisi', 'status', 'catatan_unit',
            'catatan_biro_umum', 'nomor_persetujuan', 'tanggal_persetujuan',
            'dokumen_persetujuan', 'nomor_sk_penghapusan',
            'tanggal_sk_penghapusan', 'dokumen_sk_penghapusan',
            'berita_acara_penghapusan',
        ]
        labels = {
            'tanggal_permohonan': 'Tanggal Permohonan',
            'unit_kerja': 'Unit Kerja/Satker Pemohon',
            'pemohon': 'Pegawai Pemohon/PIC Unit Kerja',
            'jenis_aset': 'Jenis Aset BMN',
            'rumah_negara': 'Rumah Negara',
            'tanah_negara': 'Tanah Negara',
            'kode_barang': 'Kode Barang',
            'nup': 'NUP',
            'nama_barang': 'Nama Barang/Aset',
            'nilai_perolehan': 'Nilai Perolehan',
            'kondisi_barang': 'Kondisi Barang',
            'lokasi_barang': 'Lokasi Barang',
            'alasan_penghapusan': 'Alasan Penghapusan',
            'dokumen_usulan': 'Dokumen Usulan Unit Kerja',
            'dokumen_pendukung': 'Dokumen Pendukung',
            'foto_kondisi': 'Foto Kondisi Aset',
            'catatan_unit': 'Catatan Unit Kerja',
            'catatan_biro_umum': 'Catatan Biro Umum',
            'nomor_persetujuan': 'Nomor Persetujuan/Penetapan',
            'tanggal_persetujuan': 'Tanggal Persetujuan/Penetapan',
            'dokumen_persetujuan': 'Dokumen Persetujuan/Penetapan',
            'nomor_sk_penghapusan': 'Nomor SK Penghapusan',
            'tanggal_sk_penghapusan': 'Tanggal SK Penghapusan',
            'dokumen_sk_penghapusan': 'Dokumen SK Penghapusan',
            'berita_acara_penghapusan': 'Berita Acara Penghapusan/Pemusnahan/Pemindahtanganan',
        }
        widgets = {
            'tanggal_permohonan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_persetujuan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tanggal_sk_penghapusan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'uraian_alasan': forms.Textarea(attrs={'rows': 4}),
            'dasar_usulan': forms.Textarea(attrs={'rows': 3}),
            'lokasi_barang': forms.Textarea(attrs={'rows': 2}),
            'catatan_unit': forms.Textarea(attrs={'rows': 3}),
            'catatan_biro_umum': forms.Textarea(attrs={'rows': 3}),
            'dokumen_usulan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            'dokumen_pendukung': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx'}),
            'foto_kondisi': forms.ClearableFileInput(attrs={'accept': 'image/*,.jpg,.jpeg,.png'}),
            'dokumen_persetujuan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            'dokumen_sk_penghapusan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            'berita_acara_penghapusan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*,.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})

        self.fields['kendaraan'].required = False
        self.fields['rumah_negara'].required = False
        self.fields['tanah_negara'].required = False
        self.fields['unit_kerja'].queryset = UnitKerja.objects.order_by('nama_unit')
        self.fields['pemohon'].queryset = Pegawai.objects.select_related('unit_kerja').order_by('nama')
        self.fields['kendaraan'].queryset = Kendaraan.objects.select_related('unit_kerja').order_by('nomor_polisi')
        self.fields['rumah_negara'].queryset = RumahDinas.objects.select_related('unit_kerja').order_by('kode_rumah')
        self.fields['tanah_negara'].queryset = TanahNegara.objects.select_related('unit_kerja').order_by('kode_tanah')

        if self.user and not is_biro_umum_user(self.user):
            unit = get_user_unit_kerja(self.user)
            if unit:
                self.fields['unit_kerja'].queryset = UnitKerja.objects.filter(pk=unit.pk)
                self.fields['unit_kerja'].initial = unit.pk
                self.fields['pemohon'].queryset = Pegawai.objects.filter(unit_kerja=unit).order_by('nama')
                self.fields['kendaraan'].queryset = Kendaraan.objects.filter(unit_kerja=unit).order_by('nomor_polisi')
                self.fields['rumah_negara'].queryset = RumahDinas.objects.filter(unit_kerja=unit).order_by('kode_rumah')
                self.fields['tanah_negara'].queryset = TanahNegara.objects.filter(unit_kerja=unit).order_by('kode_tanah')

            # Unit kerja hanya mengajukan/memperbaiki usulan, tidak mengisi bagian keputusan Biro Umum.
            biro_only_fields = [
                'status', 'catatan_biro_umum', 'nomor_persetujuan', 'tanggal_persetujuan',
                'dokumen_persetujuan', 'nomor_sk_penghapusan', 'tanggal_sk_penghapusan',
                'dokumen_sk_penghapusan', 'berita_acara_penghapusan',
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

    def clean(self):
        cleaned = super().clean()
        jenis = cleaned.get('jenis_aset')
        if jenis == 'KENDARAAN' and not cleaned.get('kendaraan'):
            raise forms.ValidationError('Untuk jenis aset Kendaraan, pilih data kendaraan yang diusulkan dihapus.')
        if jenis == 'RUMAH_NEGARA' and not cleaned.get('rumah_negara'):
            raise forms.ValidationError('Untuk jenis aset Rumah Negara, pilih data rumah negara yang diusulkan dihapus.')
        if jenis == 'TANAH_NEGARA' and not cleaned.get('tanah_negara'):
            raise forms.ValidationError('Untuk jenis aset Tanah Negara, pilih data tanah negara yang diusulkan dihapus.')
        return cleaned
