from .roles import is_admin_system, is_pengelola_bmn, is_pemeliharaan_kendaraan


def role_flags(request):
    user = getattr(request, 'user', None)
    flags = {
        'is_admin_system': False,
        'is_pengelola_bmn': False,
        'is_pemeliharaan_kendaraan': False,
        'can_access_master': False,
        'can_access_sip': False,
        'can_access_vehicle_maintenance': False,
        'can_access_house': False,
        'can_access_reports': False,
    }
    if user and user.is_authenticated:
        admin = is_admin_system(user)
        bmn = is_pengelola_bmn(user)
        pem = is_pemeliharaan_kendaraan(user)
        flags.update({
            'is_admin_system': admin,
            'is_pengelola_bmn': bmn,
            'is_pemeliharaan_kendaraan': pem,
            'can_access_master': admin or bmn,
            'can_access_sip': admin or bmn,
            'can_access_vehicle_maintenance': admin or pem,
            'can_access_house': admin or bmn,
            'can_access_reports': admin or bmn or pem,
        })
    return flags
