# Generated manually for SIKARIS role Sekretaris Jenderal

from django.db import migrations


def create_sekjen_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Sekretaris Jenderal')


def remove_sekjen_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Sekretaris Jenderal').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_loginhistory_uservisitcounter'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_sekjen_group, remove_sekjen_group),
    ]
