from django.urls import path
from . import views

app_name = 'kendaraan'

urlpatterns = [
    path('sip/', views.SIPKendaraanListView.as_view(), name='sip_list'),
    path('sip/tambah/', views.SIPKendaraanCreateView.as_view(), name='sip_create'),
    path('sip/<int:pk>/', views.SIPKendaraanDetailView.as_view(), name='sip_detail'),
    path('sip/<int:pk>/edit/', views.SIPKendaraanUpdateView.as_view(), name='sip_update'),
    path('sip/<int:pk>/hapus/', views.SIPKendaraanDeleteView.as_view(), name='sip_delete'),

    path('service/', views.ServiceKendaraanListView.as_view(), name='service_list'),
    path('service/tambah/', views.ServiceKendaraanCreateView.as_view(), name='service_create'),
    path('service/<int:pk>/', views.ServiceKendaraanDetailView.as_view(), name='service_detail'),
    path('service/<int:pk>/edit/', views.ServiceKendaraanUpdateView.as_view(), name='service_update'),
    path('service/<int:pk>/hapus/', views.ServiceKendaraanDeleteView.as_view(), name='service_delete'),
    path('service/kuitansi/<int:pk>/hapus/', views.kuitansi_service_delete, name='kuitansi_service_delete'),

    path('kondisi/', views.RiwayatKondisiListView.as_view(), name='kondisi_list'),
    path('kondisi/tambah/', views.RiwayatKondisiCreateView.as_view(), name='kondisi_create'),
    path('kondisi/<int:pk>/', views.RiwayatKondisiDetailView.as_view(), name='kondisi_detail'),
    path('kondisi/<int:pk>/hapus/', views.RiwayatKondisiDeleteView.as_view(), name='kondisi_delete'),
]
