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


class LoginHistory(models.Model):
    """Riwayat login user SIKARIS untuk pemantauan Admin System."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_histories',
    )
    login_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    session_key = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        ordering = ['-login_at']
        verbose_name = 'Riwayat Login'
        verbose_name_plural = 'Riwayat Login'

    def __str__(self):
        return f'{self.user.username} login pada {self.login_at:%d-%m-%Y %H:%M}'


class UserVisitCounter(models.Model):
    """Counter kunjungan halaman user pada aplikasi SIKARIS."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visit_counter',
    )
    total_kunjungan = models.PositiveIntegerField(default=0)
    last_visit_at = models.DateTimeField(null=True, blank=True)
    last_path = models.CharField(max_length=500, blank=True, null=True)
    last_ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_user_agent = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-total_kunjungan', 'user__username']
        verbose_name = 'Counter Kunjungan User'
        verbose_name_plural = 'Counter Kunjungan User'

    def __str__(self):
        return f'{self.user.username}: {self.total_kunjungan} kunjungan'
