from django.urls import path
from .views import (
    laporan_index,
    export_kendaraan_excel,
    export_kendaraan_pdf,
    export_rumah_excel,
    export_rumah_pdf,
)

app_name = 'laporan'

urlpatterns = [
    path('', laporan_index, name='index'),
    path('kendaraan/excel/', export_kendaraan_excel, name='kendaraan_excel'),
    path('kendaraan/pdf/', export_kendaraan_pdf, name='kendaraan_pdf'),
    path('rumah-dinas/excel/', export_rumah_excel, name='rumah_excel'),
    path('rumah-dinas/pdf/', export_rumah_pdf, name='rumah_pdf'),
]
