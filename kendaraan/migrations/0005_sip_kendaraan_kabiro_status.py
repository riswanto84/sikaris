# Generated manually for SIKARIS SIP Kendaraan approval by Kepala Biro Umum

from django.db import migrations, models


def forward_kendaraan_status_to_kabiro(apps, schema_editor):
    SIPKendaraan = apps.get_model('kendaraan', 'SIPKendaraan')
    SIPKendaraan.objects.filter(status='DIAJUKAN_SEKJEN').update(status='DIAJUKAN_KABIRO')
    SIPKendaraan.objects.filter(status='DISETUJUI_SEKJEN').update(status='DISETUJUI_KABIRO')
    SIPKendaraan.objects.filter(status='DITOLAK_SEKJEN').update(status='DITOLAK_KABIRO')


def reverse_kabiro_status_to_sekjen(apps, schema_editor):
    SIPKendaraan = apps.get_model('kendaraan', 'SIPKendaraan')
    SIPKendaraan.objects.filter(status='DIAJUKAN_KABIRO').update(status='DIAJUKAN_SEKJEN')
    SIPKendaraan.objects.filter(status='DISETUJUI_KABIRO').update(status='DISETUJUI_SEKJEN')
    SIPKendaraan.objects.filter(status='DITOLAK_KABIRO').update(status='DITOLAK_SEKJEN')


class Migration(migrations.Migration):

    dependencies = [
        ('kendaraan', '0004_sip_kendaraan_sekjen_pdf'),
    ]

    operations = [
        migrations.RunPython(forward_kendaraan_status_to_kabiro, reverse_kabiro_status_to_sekjen),
        migrations.AlterField(
            model_name='sipkendaraan',
            name='status',
            field=models.CharField(
                max_length=25,
                default='DRAFT',
                choices=[
                    ('DRAFT', 'Draft'),
                    ('DIAJUKAN', 'Diajukan'),
                    ('DIAJUKAN_SEKJEN', 'Diajukan ke Sekretaris Jenderal'),
                    ('DISETUJUI_SEKJEN', 'Disetujui Sekretaris Jenderal'),
                    ('DITOLAK_SEKJEN', 'Ditolak Sekretaris Jenderal'),
                    ('DIAJUKAN_KABIRO', 'Diajukan ke Kepala Biro Umum'),
                    ('DISETUJUI_KABIRO', 'Disetujui Kepala Biro Umum'),
                    ('DITOLAK_KABIRO', 'Ditolak Kepala Biro Umum'),
                    ('DISETUJUI', 'Disetujui'),
                    ('MENUNGGU_TTE', 'Menunggu TTE BSrE'),
                    ('AKTIF', 'Aktif'),
                    ('BERAKHIR', 'Berakhir'),
                    ('DICABUT', 'Dicabut'),
                    ('DITOLAK', 'Ditolak'),
                    ('DIBATALKAN', 'Dibatalkan'),
                ],
            ),
        ),
    ]
