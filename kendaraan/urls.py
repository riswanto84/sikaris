from django.urls import path
from . import views

app_name = 'kendaraan'

urlpatterns = [
    path('sip/', views.SIPKendaraanListView.as_view(), name='sip_list'),
    path('sip/tambah/', views.SIPKendaraanCreateView.as_view(), name='sip_create'),
    path('sip/export/<str:fmt>/', views.sip_export, name='sip_export'),
    path('sip/<int:pk>/', views.SIPKendaraanDetailView.as_view(), name='sip_detail'),
    path('sip/<int:pk>/edit/', views.SIPKendaraanUpdateView.as_view(), name='sip_update'),
    path('sip/<int:pk>/hapus/', views.SIPKendaraanDeleteView.as_view(), name='sip_delete'),
    path('sip/<int:pk>/generate-konsep-pdf/', views.sip_generate_konsep_pdf, name='sip_generate_konsep_pdf'),
    path('sip/<int:pk>/ajukan-kabiro/', views.sip_ajukan_kabiro, name='sip_ajukan_kabiro'),
    path('sip/<int:pk>/setujui-kabiro/', views.sip_setujui_kabiro, name='sip_setujui_kabiro'),
    path('sip/<int:pk>/tolak-kabiro/', views.sip_tolak_kabiro, name='sip_tolak_kabiro'),
    path('sip/<int:pk>/upload-tte-pengusul/', views.sip_upload_tte_pengusul_pdf, name='sip_upload_tte_pengusul_pdf'),
    path('sip/<int:pk>/upload-bsre/', views.sip_upload_bsre_pdf, name='sip_upload_bsre_pdf'),
    # Alias URL lama: tetap ada agar bookmark/link lama tidak error.
    path('sip/<int:pk>/ajukan-sekjen/', views.sip_ajukan_kabiro, name='sip_ajukan_sekjen'),
    path('sip/<int:pk>/setujui-sekjen/', views.sip_setujui_kabiro, name='sip_setujui_sekjen'),
    path('sip/<int:pk>/tolak-sekjen/', views.sip_tolak_kabiro, name='sip_tolak_sekjen'),
    path('persetujuan-kabiro/sip-kendaraan/', views.KepalaBiroUmumSIPKendaraanListView.as_view(), name='kabiro_sip_kendaraan_list'),
    path('persetujuan-sekjen/sip-kendaraan/', views.KepalaBiroUmumSIPKendaraanListView.as_view(), name='sekjen_sip_kendaraan_list'),

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
