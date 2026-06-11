# Generated manually for SIKARIS user profile unit kerja

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master', '0004_alter_jenis_kendaraan_choices'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_kerja', models.ForeignKey(blank=True, help_text='Unit kerja yang boleh diakses user ini.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_profiles', to='master.unitkerja')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil User',
                'verbose_name_plural': 'Profil User',
            },
        ),
    ]
