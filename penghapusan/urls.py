from django.urls import path
from . import views

app_name = 'penghapusan'

urlpatterns = [
    path('export/<str:fmt>/', views.export_penghapusan, name='export'),
    path('', views.PermohonanPenghapusanListView.as_view(), name='list'),
    path('verifikasi/', views.VerifikasiPenghapusanListView.as_view(), name='verifikasi'),
    path('persetujuan-sekjen/', views.PersetujuanSekjenPenghapusanListView.as_view(), name='persetujuan_sekjen'),
    path('persetujuan-dirjen-rehsos/', views.PersetujuanDirjenRehsosPenghapusanListView.as_view(), name='persetujuan_dirjen_rehsos'),
    path('tambah/', views.PermohonanPenghapusanCreateView.as_view(), name='create'),
    path('template-import-barang/', views.DownloadTemplateBarangPenghapusanView.as_view(), name='template_import_barang'),
    path('<int:pk>/', views.PermohonanPenghapusanDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PermohonanPenghapusanUpdateView.as_view(), name='update'),
    path('<int:pk>/proses/', views.ProsesPenghapusanView.as_view(), name='proses'),
    path('<int:pk>/import-barang/', views.ImportBarangPenghapusanView.as_view(), name='import_barang'),
    path('<int:pk>/hapus/', views.PermohonanPenghapusanDeleteView.as_view(), name='delete'),
]
