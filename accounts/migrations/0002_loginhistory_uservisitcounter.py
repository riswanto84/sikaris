# Generated manually for SIKARIS login history and user visit counter

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('session_key', models.CharField(blank=True, max_length=80, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='login_histories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Riwayat Login',
                'verbose_name_plural': 'Riwayat Login',
                'ordering': ['-login_at'],
            },
        ),
        migrations.CreateModel(
            name='UserVisitCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_kunjungan', models.PositiveIntegerField(default=0)),
                ('last_visit_at', models.DateTimeField(blank=True, null=True)),
                ('last_path', models.CharField(blank=True, max_length=500, null=True)),
                ('last_ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('last_user_agent', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='visit_counter', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Counter Kunjungan User',
                'verbose_name_plural': 'Counter Kunjungan User',
                'ordering': ['-total_kunjungan', 'user__username'],
            },
        ),
    ]
