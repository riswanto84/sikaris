# Generated for multi-photo kendaraan support
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FotoKendaraan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('foto', models.ImageField(upload_to='kendaraan/galeri/')),
                ('keterangan', models.CharField(blank=True, max_length=200, null=True)),
                ('diupload_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('kendaraan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='galeri_foto', to='master.kendaraan')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
