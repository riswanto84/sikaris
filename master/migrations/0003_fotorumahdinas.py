# Generated for multi-photo rumah dinas support
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master', '0002_fotokendaraan'),
    ]

    operations = [
        migrations.CreateModel(
            name='FotoRumahDinas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('foto', models.ImageField(upload_to='rumah_dinas/galeri/')),
                ('keterangan', models.CharField(blank=True, max_length=200, null=True)),
                ('diupload_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('rumah_dinas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='galeri_foto', to='master.rumahdinas')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Foto Rumah Dinas',
                'verbose_name_plural': 'Foto Rumah Dinas',
            },
        ),
    ]
