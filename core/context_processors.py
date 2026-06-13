from .roles import is_admin_system, is_pengelola_bmn, is_pemeliharaan_kendaraan
from .access import is_biro_umum_user, get_user_unit_kerja
from .notifications import build_notifications


def role_flags(request):
    user = getattr(request, 'user', None)
    flags = {
        'is_admin_system': False,
        'is_pengelola_bmn': False,
        'is_pemeliharaan_kendaraan': False,
        'is_pemeliharaan_strict': False,
        'is_maintenance_restricted': False,
        'can_access_master': False,
        'can_access_sip': False,
        'can_access_vehicle_maintenance': False,
        'can_access_house': False,
        'can_access_reports': False,
        'can_access_report_kendaraan': False,
        'can_access_report_rumah': False,
        'can_access_penghapusan': False,
        'can_access_psp': False,
        'is_biro_umum': False,
        'user_unit_kerja': None,
        'notification_count': 0,
        'notification_items': [],
        'notification_has_more': False,
    }

    if user and user.is_authenticated:
        admin = is_admin_system(user)
        bmn = is_pengelola_bmn(user)
        pem = is_pemeliharaan_kendaraan(user)
        biro = is_biro_umum_user(user)
        unit = get_user_unit_kerja(user)

        # FINAL STRICT:
        # User dengan role Pemeliharaan Kendaraan harus dibatasi menu,
        # walaupun unit kerjanya Biro Umum atau memiliki flag Biro Umum dari unit kerja.
        # Hanya superuser/Admin System yang tidak dibatasi.
        pemeliharaan_strict = pem and not admin and not user.is_superuser

        flags.update(build_notifications(user))
        flags.update({
            'is_admin_system': admin,
            'is_pengelola_bmn': bmn,
            'is_pemeliharaan_kendaraan': pem,
            'is_pemeliharaan_strict': pemeliharaan_strict,
            'is_maintenance_restricted': pemeliharaan_strict,
            'is_biro_umum': biro,
            'user_unit_kerja': unit,

            # Menu/fitur non-pemeliharaan dipaksa False untuk role Pemeliharaan.
            'can_access_master': False if pemeliharaan_strict else (admin or bmn or biro),
            'can_access_sip': False if pemeliharaan_strict else (admin or bmn or biro),
            'can_access_vehicle_maintenance': admin or pem or biro,
            'can_access_house': False if pemeliharaan_strict else (admin or bmn or biro),
            'can_access_penghapusan': False if pemeliharaan_strict else (admin or bmn or biro),
            'can_access_psp': False if pemeliharaan_strict else (admin or bmn or biro),

            # Pemeliharaan boleh masuk halaman laporan, tetapi hanya bagian kendaraan/service.
            'can_access_reports': admin or bmn or pem or biro,
            'can_access_report_kendaraan': admin or bmn or pem or biro,
            'can_access_report_rumah': False if pemeliharaan_strict else (admin or bmn or biro),
        })

    return flags
