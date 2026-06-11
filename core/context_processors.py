from .roles import is_admin_system, is_pengelola_bmn, is_pemeliharaan_kendaraan
from .access import is_biro_umum_user, get_user_unit_kerja


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
        'is_biro_umum': False,
        'user_unit_kerja': None,
    }
    if user and user.is_authenticated:
        admin = is_admin_system(user)
        bmn = is_pengelola_bmn(user)
        pem = is_pemeliharaan_kendaraan(user)
        biro = is_biro_umum_user(user)
        unit = get_user_unit_kerja(user)
        flags.update({
            'is_admin_system': admin,
            'is_pengelola_bmn': bmn,
            'is_pemeliharaan_kendaraan': pem,
            'is_biro_umum': biro,
            'user_unit_kerja': unit,
            'can_access_master': admin or bmn or biro,
            'can_access_sip': admin or bmn or biro,
            'can_access_vehicle_maintenance': admin or pem or biro,
            'can_access_house': admin or bmn or biro,
            'can_access_reports': admin or bmn or pem or biro,
        })
    return flags
