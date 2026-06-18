from django.contrib import admin
from .models import SIPBarangLainnya, SIPBarangLainnyaItem

class ItemInline(admin.TabularInline):
    model = SIPBarangLainnyaItem
    extra = 0

@admin.register(SIPBarangLainnya)
class SIPBarangLainnyaAdmin(admin.ModelAdmin):
    list_display = ('nomor_sip', 'tanggal_sip', 'pemegang_sip', 'status')
    search_fields = ('nomor_sip', 'pemegang_sip__nama', 'nama_pejabat_penandatangan')
    inlines = [ItemInline]
