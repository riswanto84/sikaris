from django.urls import path
from . import views

app_name = 'penghapusan'

urlpatterns = [
    path('', views.PermohonanPenghapusanListView.as_view(), name='list'),
    path('tambah/', views.PermohonanPenghapusanCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PermohonanPenghapusanDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PermohonanPenghapusanUpdateView.as_view(), name='update'),
    path('<int:pk>/hapus/', views.PermohonanPenghapusanDeleteView.as_view(), name='delete'),
]
