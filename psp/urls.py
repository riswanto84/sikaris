from django.urls import path
from . import views

app_name = 'psp'

urlpatterns = [
    path('', views.PermohonanPSPListView.as_view(), name='list'),
    path('tambah/', views.PermohonanPSPCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PermohonanPSPDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PermohonanPSPUpdateView.as_view(), name='update'),
    path('<int:pk>/hapus/', views.PermohonanPSPDeleteView.as_view(), name='delete'),
]
