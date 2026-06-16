# Generated manually for SIKARIS role Kepala Biro Umum

from django.db import migrations


def create_kepala_biro_umum_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Kepala Biro Umum')


def remove_kepala_biro_umum_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Kepala Biro Umum').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_create_sekjen_group'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_kepala_biro_umum_group, remove_kepala_biro_umum_group),
    ]
