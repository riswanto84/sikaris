from django.urls import path
from .views import laporan_index
app_name='laporan'
urlpatterns=[path('', laporan_index, name='index')]
