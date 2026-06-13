from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('master/', include('master.urls')),
    path('kendaraan/', include('kendaraan.urls')),
    path('rumah-dinas/', include('rumah_dinas.urls')),
    path('tanah-negara/', include('tanah_negara.urls')),
    path('penghapusan-bmn/', include('penghapusan.urls')),
    path('psp-bmn/', include('psp.urls')),
    path('laporan/', include('laporan.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
