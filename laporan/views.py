from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from core.roles import can_view_reports
from master.models import Kendaraan, RumahDinas, Pegawai
from kendaraan.models import SIPKendaraan, ServiceKendaraan
from rumah_dinas.models import SIPRumahDinas


@login_required
@user_passes_test(can_view_reports, login_url='login')
def laporan_index(request):
    return render(request, 'laporan/index.html', {
        'kendaraan': Kendaraan.objects.count(),
        'rumah': RumahDinas.objects.count(),
        'pegawai': Pegawai.objects.count(),
        'sip_kendaraan': SIPKendaraan.objects.count(),
        'sip_rumah': SIPRumahDinas.objects.count(),
        'service': ServiceKendaraan.objects.count(),
    })
