from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User


class Command(BaseCommand):
    help = 'Membuat role dan user demo SIKARIS'

    def handle(self, *args, **kwargs):
        roles = ['Admin System', 'Pengelola BMN', 'Pemeliharaan Kendaraan', 'Biro Umum']
        for role in roles:
            Group.objects.get_or_create(name=role)

        demos = [
            ('adminsystem', 'Admin System', True),
            ('biroumum', 'Biro Umum', False),
            ('bmn', 'Pengelola BMN', False),
            ('pemeliharaan', 'Pemeliharaan Kendaraan', False),
        ]
        for username, group_name, is_super in demos:
            user, _created = User.objects.get_or_create(username=username)
            user.set_password('Password123!')
            user.is_staff = True
            user.is_superuser = is_super
            user.email = f'{username}@example.local'
            user.save()
            user.groups.add(Group.objects.get(name=group_name))
            self.stdout.write(self.style.SUCCESS(f'User siap: {username} / Password123! / role {group_name}'))
