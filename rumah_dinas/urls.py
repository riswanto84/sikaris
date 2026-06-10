from django.urls import path
from . import views
app_name='rumah_dinas'
urlpatterns=[
    path('sip/', views.SIPRumahDinasListView.as_view(), name='sip_list'),
    path('sip/tambah/', views.SIPRumahDinasCreateView.as_view(), name='sip_create'),
    path('sip/<int:pk>/edit/', views.SIPRumahDinasUpdateView.as_view(), name='sip_update'),
]
