from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.roles import is_admin_system, is_pengelola_bmn, is_pemeliharaan_kendaraan
from core.access import is_biro_umum_user


class Command(BaseCommand):
    help = 'Cek role dan flag akses user SIKARIS.'

    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, *args, **options):
        username = options['username']
        User = get_user_model()
        user = User.objects.get(username=username)

        admin = is_admin_system(user)
        bmn = is_pengelola_bmn(user)
        pem = is_pemeliharaan_kendaraan(user)
        biro = is_biro_umum_user(user)
        strict = pem and not admin and not user.is_superuser

        self.stdout.write(f'Username: {user.username}')
        self.stdout.write(f'Groups: {", ".join(user.groups.values_list("name", flat=True)) or "-"}')
        self.stdout.write(f'is_superuser: {user.is_superuser}')
        self.stdout.write(f'is_admin_system: {admin}')
        self.stdout.write(f'is_pengelola_bmn: {bmn}')
        self.stdout.write(f'is_pemeliharaan_kendaraan: {pem}')
        self.stdout.write(f'is_biro_umum_user: {biro}')
        self.stdout.write(self.style.SUCCESS(f'is_pemeliharaan_strict: {strict}'))
