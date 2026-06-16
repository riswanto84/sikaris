from django.urls import path
from . import views
app_name='rumah_dinas'
urlpatterns=[
    path('sip/export/<str:fmt>/', views.export_sip_rumah, name='sip_export'),
    path('persetujuan-sekjen/sip-rumah/export/<str:fmt>/', views.export_persetujuan_sip_rumah, name='sekjen_sip_rumah_export'),
    path('sip/', views.SIPRumahDinasListView.as_view(), name='sip_list'),
    path('sip/tambah/', views.SIPRumahDinasCreateView.as_view(), name='sip_create'),
    path('sip/<int:pk>/', views.SIPRumahDinasDetailView.as_view(), name='sip_detail'),
    path('sip/<int:pk>/edit/', views.SIPRumahDinasUpdateView.as_view(), name='sip_update'),
    path('sip/<int:pk>/hapus/', views.SIPRumahDinasDeleteView.as_view(), name='sip_delete'),
    path('sip/<int:pk>/generate-konsep-pdf/', views.sip_generate_konsep_pdf, name='sip_generate_konsep_pdf'),
    path('sip/<int:pk>/upload-tte-calon-pengguna/', views.sip_upload_tte_calon_pengguna_pdf, name='sip_upload_tte_calon_pengguna_pdf'),
    path('sip/<int:pk>/ajukan-sekjen/', views.sip_ajukan_sekjen, name='sip_ajukan_sekjen'),
    path('sip/<int:pk>/setujui-sekjen/', views.sip_setujui_sekjen, name='sip_setujui_sekjen'),
    path('sip/<int:pk>/tolak-sekjen/', views.sip_tolak_sekjen, name='sip_tolak_sekjen'),
    path('sip/<int:pk>/upload-tte-sekjen/', views.sip_upload_tte_sekjen_pdf, name='sip_upload_tte_sekjen_pdf'),
    path('persetujuan-sekjen/sip-rumah/', views.SekjenSIPRumahListView.as_view(), name='sekjen_sip_rumah_list'),
]
