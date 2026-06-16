from django.contrib import admin
from .models import BarangPSP, FotoBarangPSP, PermohonanPSPBMN


class BarangPSPInline(admin.TabularInline):
    model = BarangPSP
    extra = 0
    fields = ('nomor_urut', 'kode_barang', 'nup', 'nama_barang', 'tipe_barang', 'tahun_perolehan', 'kuantitas', 'nilai_perolehan', 'kondisi_barang')


@admin.register(PermohonanPSPBMN)
class PermohonanPSPBMNAdmin(admin.ModelAdmin):
    list_display = ('nomor_permohonan', 'tanggal_permohonan', 'unit_kerja', 'jenis_barang', 'jumlah_barang', 'total_nilai_barang', 'nomor_tiket_siman', 'status', 'status_tte')
    list_filter = ('jenis_barang', 'status', 'status_tte', 'status_emeterai', 'tanggal_permohonan')
    search_fields = ('nomor_permohonan', 'judul_paket', 'nama_barang', 'kode_barang', 'nup', 'nomor_tiket_siman', 'nomor_sk_psp', 'nomor_nota_permohonan_psp')
    inlines = [BarangPSPInline]


@admin.register(BarangPSP)
class BarangPSPAdmin(admin.ModelAdmin):
    list_display = ('permohonan', 'nomor_urut', 'kode_barang', 'nup', 'nama_barang', 'kuantitas', 'nilai_perolehan', 'kondisi_barang')
    search_fields = ('permohonan__nomor_permohonan', 'kode_barang', 'nup', 'nama_barang', 'tipe_barang')
    list_filter = ('kondisi_barang',)


@admin.register(FotoBarangPSP)
class FotoBarangPSPAdmin(admin.ModelAdmin):
    list_display = ('permohonan', 'keterangan', 'created_at')
    search_fields = ('permohonan__nomor_permohonan', 'keterangan')
