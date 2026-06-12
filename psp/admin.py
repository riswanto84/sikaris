from django.contrib import admin
from .models import PermohonanPSPBMN


@admin.register(PermohonanPSPBMN)
class PermohonanPSPBMNAdmin(admin.ModelAdmin):
    list_display = ('nomor_permohonan', 'tanggal_permohonan', 'unit_kerja', 'jenis_barang', 'nama_barang', 'nilai_psp', 'status')
    list_filter = ('status', 'jenis_barang', 'unit_kerja')
    search_fields = ('nomor_permohonan', 'nama_barang', 'kode_barang', 'nup', 'nomor_penetapan_psp')
