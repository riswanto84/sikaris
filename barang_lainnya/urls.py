from django.urls import path
from . import views

app_name = 'barang_lainnya'

urlpatterns = [
    path('sip/', views.sip_list, name='sip_list'),
    path('sip/tambah/', views.sip_create, name='sip_create'),
    path('sip/<int:pk>/', views.sip_detail, name='sip_detail'),
    path('sip/<int:pk>/edit/', views.sip_update, name='sip_update'),
    path('sip/<int:pk>/teruskan/', views.sip_teruskan, name='sip_teruskan'),
    path('sip/<int:pk>/setujui/', views.sip_setujui, name='sip_setujui'),
    path('sip/<int:pk>/tolak/', views.sip_tolak, name='sip_tolak'),
    path('sip/<int:pk>/generate-konsep-pdf/', views.sip_generate_konsep_pdf, name='sip_generate_konsep_pdf'),
    path('sip/export/<str:fmt>/', views.sip_export, name='sip_export'),
    path('persetujuan/sip/', views.sip_persetujuan_list, name='persetujuan_list'),
]
