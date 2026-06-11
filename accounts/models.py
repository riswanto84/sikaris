from django.conf import settings
from django.db import models

from master.models import UnitKerja


class UserProfile(models.Model):
    """Profil tambahan user aplikasi SIKARIS.

    Field unit_kerja dipakai sebagai dasar pembatasan akses data untuk user non-Biro Umum.
    Biro Umum/superuser tetap dapat mengakses seluruh data seluruh satker.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    unit_kerja = models.ForeignKey(
        UnitKerja,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        help_text='Unit kerja yang boleh diakses user ini.',
    )

    class Meta:
        verbose_name = 'Profil User'
        verbose_name_plural = 'Profil User'

    def __str__(self):
        unit = self.unit_kerja.nama_unit if self.unit_kerja else 'Tanpa unit kerja'
        return f'{self.user.username} - {unit}'
