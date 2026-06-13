from django.contrib import admin
from .models import SIPRumahDinas, PerbaikanRumahDinas
@admin.register(SIPRumahDinas)
class SIPRumahAdmin(admin.ModelAdmin):
    list_display=['nomor_sip','tanggal_sip','rumah_dinas','pegawai','tanggal_mulai','tanggal_akhir','status']
    list_filter=['status','tanggal_sip']
    search_fields=['nomor_sip','rumah_dinas__nama_rumah','pegawai__nama']
@admin.register(PerbaikanRumahDinas)
class PerbaikanAdmin(admin.ModelAdmin):
    list_display=['rumah_dinas','tanggal_laporan','jenis_kerusakan','status','realisasi_biaya']
    list_filter=['status']
