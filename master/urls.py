from django.urls import path
from . import views

app_name = 'master'

urlpatterns = [
    path('unit-kerja/', views.UnitKerjaListView.as_view(), name='unitkerja_list'),
    path('unit-kerja/tambah/', views.UnitKerjaCreateView.as_view(), name='unitkerja_create'),
    path('unit-kerja/<int:pk>/edit/', views.UnitKerjaUpdateView.as_view(), name='unitkerja_update'),

    path('pegawai/', views.PegawaiListView.as_view(), name='pegawai_list'),
    path('pegawai/tambah/', views.PegawaiCreateView.as_view(), name='pegawai_create'),
    path('pegawai/<int:pk>/edit/', views.PegawaiUpdateView.as_view(), name='pegawai_update'),
    path('pegawai/<int:pk>/foto/hapus/', views.pegawai_foto_delete, name='pegawai_foto_delete'),

    path('kendaraan/', views.KendaraanListView.as_view(), name='kendaraan_list'),
    path('kendaraan/tambah/', views.KendaraanCreateView.as_view(), name='kendaraan_create'),
    path('kendaraan/<int:pk>/edit/', views.KendaraanUpdateView.as_view(), name='kendaraan_update'),
    path('kendaraan/foto/<int:pk>/hapus/', views.kendaraan_foto_delete, name='kendaraan_foto_delete'),

    path('rumah-dinas/', views.RumahDinasListView.as_view(), name='rumah_list'),
    path('rumah-dinas/tambah/', views.RumahDinasCreateView.as_view(), name='rumah_create'),
    path('rumah-dinas/<int:pk>/edit/', views.RumahDinasUpdateView.as_view(), name='rumah_update'),
    path('rumah-dinas/foto/<int:pk>/hapus/', views.rumah_foto_delete, name='rumah_foto_delete'),
]
