from django.db import migrations


def normalize_status_forward(apps, schema_editor):
    SIPKendaraan = apps.get_model('kendaraan', 'SIPKendaraan')
    mapping = {
        'DIAJUKAN_KABIRO': 'DIAJUKAN',
        'DIAJUKAN_SEKJEN': 'DIAJUKAN',
        'DISETUJUI_KABIRO': 'DISETUJUI',
        'DISETUJUI_SEKJEN': 'DISETUJUI',
        'DITOLAK_KABIRO': 'DITOLAK',
        'DITOLAK_SEKJEN': 'DITOLAK',
        'AKTIF': 'TERBIT',
        'DICABUT': 'DIBATALKAN',
    }
    for old, new in mapping.items():
        SIPKendaraan.objects.filter(status=old).update(status=new)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('kendaraan', '0005_sip_kendaraan_kabiro_status'),
    ]

    operations = [
        migrations.RunPython(normalize_status_forward, noop_reverse),
    ]
