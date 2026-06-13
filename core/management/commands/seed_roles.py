from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

from accounts.models import UserProfile
from master.models import UnitKerja


class Command(BaseCommand):
    help = 'Membuat role dan user demo SIKARIS'

    def handle(self, *args, **kwargs):
        roles = ['Admin System', 'Pengelola BMN', 'Pemeliharaan Kendaraan', 'Biro Umum']
        for role in roles:
            Group.objects.get_or_create(name=role)

        biro_umum_unit, _ = UnitKerja.objects.get_or_create(
            nama_unit='Biro Umum',
            defaults={'keterangan': 'Unit kerja pusat dengan akses seluruh satker.'},
        )
        unit_demo, _ = UnitKerja.objects.get_or_create(
            nama_unit='Unit Kerja Demo',
            defaults={'keterangan': 'Unit kerja contoh untuk user non-Biro Umum.'},
        )

        demos = [
            ('adminsystem', 'Admin System', True, None),
            ('biroumum', 'Biro Umum', False, biro_umum_unit),
            ('bmn', 'Pengelola BMN', False, unit_demo),
            ('pemeliharaan', 'Pemeliharaan Kendaraan', False, unit_demo),
        ]
        for username, group_name, is_super, unit_kerja in demos:
            user, _created = User.objects.get_or_create(username=username)
            user.set_password('Password123!')
            user.is_staff = True
            user.is_superuser = is_super
            user.email = f'{username}@example.local'
            user.save()
            user.groups.add(Group.objects.get(name=group_name))
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'unit_kerja': unit_kerja},
            )
            unit_label = unit_kerja.nama_unit if unit_kerja else 'Akses penuh/superuser'
            self.stdout.write(self.style.SUCCESS(
                f'User siap: {username} / Password123! / role {group_name} / unit {unit_label}'
            ))
