from django.contrib import admin
from .models import SIPKendaraan, ServiceKendaraan, RiwayatKondisiKendaraan
@admin.register(SIPKendaraan)
class SIPKendaraanAdmin(admin.ModelAdmin):
    list_display=['nomor_sip','tanggal_sip','kendaraan','pegawai','tanggal_mulai','tanggal_akhir','status']
    list_filter=['status','tanggal_sip']
    search_fields=['nomor_sip','kendaraan__nomor_polisi','pegawai__nama','pegawai__nip']
@admin.register(ServiceKendaraan)
class ServiceAdmin(admin.ModelAdmin):
    list_display=['kendaraan','tanggal_service','jenis_service','kilometer','total_biaya','kondisi_sesudah']
    list_filter=['jenis_service','kondisi_sesudah']
@admin.register(RiwayatKondisiKendaraan)
class RiwayatKondisiAdmin(admin.ModelAdmin):
    list_display=['kendaraan','tanggal','kondisi','dicatat_oleh']
    list_filter=['kondisi']
