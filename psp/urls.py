from django.urls import path
from . import views

app_name = 'psp'

urlpatterns = [
    path('', views.PermohonanPSPListView.as_view(), name='list'),
    path('verifikasi/', views.VerifikasiPSPListView.as_view(), name='verifikasi'),
    path('persetujuan-sekjen/', views.PersetujuanSekjenPSPListView.as_view(), name='persetujuan_sekjen'),
    path('tambah/', views.PermohonanPSPCreateView.as_view(), name='create'),
    path('template-import-barang/', views.DownloadTemplateBarangPSPView.as_view(), name='template_import_barang'),
    path('<int:pk>/', views.PermohonanPSPDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PermohonanPSPUpdateView.as_view(), name='update'),
    path('<int:pk>/proses/', views.ProsesPSPView.as_view(), name='proses'),
    path('<int:pk>/generate-dokumen/<str:jenis>/', views.GenerateDokumenPSPView.as_view(), name='generate_dokumen'),
    path('<int:pk>/hapus/', views.PermohonanPSPDeleteView.as_view(), name='delete'),
    path('<int:pk>/import-barang/', views.ImportBarangPSPView.as_view(), name='import_barang'),
    path('<int:pk>/export-lampiran-pdf/', views.ExportLampiranPSPPDFView.as_view(), name='export_lampiran_pdf'),
]
