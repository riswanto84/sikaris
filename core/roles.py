from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test

ADMIN_SYSTEM = 'Admin System'
PENGELOLA_BMN = 'Pengelola BMN'
PEMELIHARAAN_KENDARAAN = 'Pemeliharaan Kendaraan'


def has_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def is_admin_system(user):
    return user.is_authenticated and (user.is_superuser or has_group(user, ADMIN_SYSTEM))


def is_pengelola_bmn(user):
    return user.is_authenticated and has_group(user, PENGELOLA_BMN)


def is_pemeliharaan_kendaraan(user):
    return user.is_authenticated and has_group(user, PEMELIHARAAN_KENDARAAN)


def can_manage_master(user):
    return is_admin_system(user) or is_pengelola_bmn(user)


def can_manage_sip(user):
    return is_admin_system(user) or is_pengelola_bmn(user)


def can_manage_vehicle_maintenance(user):
    return is_admin_system(user) or is_pemeliharaan_kendaraan(user)


def can_view_vehicle(user):
    return is_admin_system(user) or is_pengelola_bmn(user) or is_pemeliharaan_kendaraan(user)


def can_view_reports(user):
    return is_admin_system(user) or is_pengelola_bmn(user) or is_pemeliharaan_kendaraan(user)


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
    allowed_roles = [ADMIN_SYSTEM, PENGELOLA_BMN]


class MaintenanceRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, PEMELIHARAAN_KENDARAAN]


class VehicleViewRequiredMixin(RoleRequiredMixin):
    allowed_roles = [ADMIN_SYSTEM, PENGELOLA_BMN, PEMELIHARAAN_KENDARAAN]


def bmn_required(view_func):
    return user_passes_test(can_manage_master, login_url='login')(view_func)


def maintenance_required(view_func):
    return user_passes_test(can_manage_vehicle_maintenance, login_url='login')(view_func)
