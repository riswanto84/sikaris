from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test

ADMIN_SYSTEM = 'Admin System'
PENGELOLA_BMN = 'Pengelola BMN'
PEMELIHARAAN_KENDARAAN = 'Pemeliharaan Kendaraan'
BIRO_UMUM = 'Biro Umum'
SEKRETARIS_JENDERAL = 'Sekretaris Jenderal'
KEPALA_BIRO_UMUM = 'Kepala Biro Umum'
PEJABAT_PENERBIT_SIP = 'Pejabat Penerbit SIP'
SEKRETARIS_DITJEN = 'Sekretaris Ditjen'
SEKRETARIS_ESELON_I = 'Sekretaris Eselon I'
KEPALA_SENTRA = 'Kepala Sentra'
KEPALA_BALAI = 'Kepala Balai'
SEKRETARIS_UKE_II = 'Sekretaris UKE II'
DIRJEN_REHSOS = 'Direktur Jenderal Rehabilitasi Sosial'


def has_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def is_admin_system(user):
    return user.is_authenticated and (user.is_superuser or has_group(user, ADMIN_SYSTEM))


def is_pengelola_bmn(user):
    return user.is_authenticated and has_group(user, PENGELOLA_BMN)


def is_pemeliharaan_kendaraan(user):
    return user.is_authenticated and has_group(user, PEMELIHARAAN_KENDARAAN)


def is_sekretaris_jenderal(user):
    return user.is_authenticated and has_group(user, SEKRETARIS_JENDERAL)


def is_kepala_biro_umum(user):
    return user.is_authenticated and has_group(user, KEPALA_BIRO_UMUM)


def is_dirjen_rehsos(user):
    return user.is_authenticated and has_group(user, DIRJEN_REHSOS)

def is_pejabat_penerbit_sip(user):
    return user.is_authenticated and user.groups.filter(name__in=[PEJABAT_PENERBIT_SIP, SEKRETARIS_DITJEN, SEKRETARIS_ESELON_I, SEKRETARIS_UKE_II, KEPALA_SENTRA, KEPALA_BALAI]).exists()


def can_manage_master(user):
    from core.access import is_biro_umum_user
    return is_admin_system(user) or is_pengelola_bmn(user) or is_biro_umum_user(user)


def can_manage_sip(user):
    from core.access import is_biro_umum_user
    return is_admin_system(user) or is_pengelola_bmn(user) or is_biro_umum_user(user)


def can_edit_sip(user):
    from core.access import is_biro_umum_user
    return can_manage_sip(user) or is_sekretaris_jenderal(user) or is_kepala_biro_umum(user)


def can_approve_sip(user):
    return is_admin_system(user) or is_sekretaris_jenderal(user) or is_kepala_biro_umum(user)


def can_approve_sip_rumah(user):
    return is_admin_system(user) or is_sekretaris_jenderal(user)


def can_approve_sip_kendaraan(user):
    return is_admin_system(user) or is_kepala_biro_umum(user) or is_pejabat_penerbit_sip(user)

def can_approve_sip_kendaraan_object(user, sip):
    if is_admin_system(user):
        return True
    from kendaraan.sip_penerbit import user_is_penerbit_for_sip
    return user_is_penerbit_for_sip(user, sip)


def can_manage_vehicle_maintenance(user):
    return is_admin_system(user) or is_pemeliharaan_kendaraan(user)


def can_view_vehicle(user):
    from core.access import is_biro_umum_user
    return is_admin_system(user) or is_pengelola_bmn(user) or is_pemeliharaan_kendaraan(user) or is_biro_umum_user(user)


def can_view_reports(user):
    from core.access import is_biro_umum_user
    return is_admin_system(user) or is_pengelola_bmn(user) or is_pemeliharaan_kendaraan(user) or is_biro_umum_user(user)


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []
    allow_superuser = True

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if self.allow_superuser and user.is_superuser:
            return True
        return user.groups.filter(name__in=self.allowed_roles).exists()


class AdminSystemRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM]


class BMNRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, PENGELOLA_BMN, BIRO_UMUM]


class SekjenRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, SEKRETARIS_JENDERAL]


class KepalaBiroUmumRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, KEPALA_BIRO_UMUM, PEJABAT_PENERBIT_SIP, SEKRETARIS_DITJEN, SEKRETARIS_ESELON_I, SEKRETARIS_UKE_II, KEPALA_SENTRA, KEPALA_BALAI]


class SIPEditRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, PENGELOLA_BMN, BIRO_UMUM, SEKRETARIS_JENDERAL, KEPALA_BIRO_UMUM, PEJABAT_PENERBIT_SIP, SEKRETARIS_DITJEN, SEKRETARIS_ESELON_I, SEKRETARIS_UKE_II, KEPALA_SENTRA, KEPALA_BALAI]


class SIPApprovalRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, SEKRETARIS_JENDERAL, KEPALA_BIRO_UMUM]


class MaintenanceRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, PEMELIHARAAN_KENDARAAN]


class VehicleViewRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, PENGELOLA_BMN, PEMELIHARAAN_KENDARAAN, BIRO_UMUM, SEKRETARIS_JENDERAL, KEPALA_BIRO_UMUM, PEJABAT_PENERBIT_SIP, SEKRETARIS_DITJEN, SEKRETARIS_ESELON_I, SEKRETARIS_UKE_II, KEPALA_SENTRA, KEPALA_BALAI]


def bmn_required(view_func):
    return user_passes_test(can_manage_master, login_url='login')(view_func)


def sekjen_required(view_func):
    return user_passes_test(can_approve_sip_rumah, login_url='login')(view_func)


def kepala_biro_umum_required(view_func):
    return user_passes_test(can_approve_sip_kendaraan, login_url='login')(view_func)


def maintenance_required(view_func):
    return user_passes_test(can_manage_vehicle_maintenance, login_url='login')(view_func)
