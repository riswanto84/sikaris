from django.contrib import admin
from .models import UnitKerja, Pegawai, Kendaraan, FotoKendaraan, RumahDinas, FotoRumahDinas


@admin.register(UnitKerja)
class UnitKerjaAdmin(admin.ModelAdmin):
    search_fields = ['nama_unit']


@admin.register(Pegawai)
class PegawaiAdmin(admin.ModelAdmin):
    list_display = ['nip', 'nama', 'jabatan', 'unit_kerja', 'status_pegawai']
    search_fields = ['nip', 'nama', 'jabatan']
    list_filter = ['unit_kerja', 'status_pegawai']


class FotoKendaraanInline(admin.TabularInline):
    model = FotoKendaraan
    extra = 1


@admin.register(Kendaraan)
class KendaraanAdmin(admin.ModelAdmin):
    list_display = ['nomor_polisi', 'merek', 'tipe', 'kondisi', 'status_pemanfaatan', 'pengguna']
    search_fields = ['nomor_polisi', 'merek', 'tipe', 'nomor_rangka', 'nomor_mesin']
    list_filter = ['kondisi', 'status_pemanfaatan', 'jenis_kendaraan']
    inlines = [FotoKendaraanInline]


@admin.register(FotoKendaraan)
class FotoKendaraanAdmin(admin.ModelAdmin):
    list_display = ['kendaraan', 'foto', 'created_at', 'diupload_oleh']
    search_fields = ['kendaraan__nomor_polisi', 'kendaraan__merek']


class FotoRumahDinasInline(admin.TabularInline):
    model = FotoRumahDinas
    extra = 1


@admin.register(RumahDinas)
class RumahDinasAdmin(admin.ModelAdmin):
    list_display = ['kode_rumah', 'nama_rumah', 'kabupaten_kota', 'kondisi', 'status_pemanfaatan']
    search_fields = ['kode_rumah', 'nama_rumah', 'alamat']
    list_filter = ['kondisi', 'status_pemanfaatan', 'kabupaten_kota']
    inlines = [FotoRumahDinasInline]


@admin.register(FotoRumahDinas)
class FotoRumahDinasAdmin(admin.ModelAdmin):
    list_display = ['rumah_dinas', 'foto', 'created_at', 'diupload_oleh']
    search_fields = ['rumah_dinas__kode_rumah', 'rumah_dinas__nama_rumah', 'rumah_dinas__alamat']
