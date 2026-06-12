from django.urls import path
from . import views
app_name = 'tanah_negara'
urlpatterns = [
    path('', views.TanahNegaraListView.as_view(), name='list'),
    path('tambah/', views.TanahNegaraCreateView.as_view(), name='create'),
    path('import/', views.TanahNegaraImportView.as_view(), name='import'),
    path('<int:pk>/', views.TanahNegaraDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TanahNegaraUpdateView.as_view(), name='update'),
    path('<int:pk>/hapus/', views.TanahNegaraDeleteView.as_view(), name='delete'),
]
