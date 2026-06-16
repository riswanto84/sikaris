from django.core.management.base import BaseCommand

from kendaraan.models import SIPKendaraan
from kendaraan.sip_penerbit import apply_snapshot_penerbit_sip_kendaraan


class Command(BaseCommand):
    help = 'Mengisi ulang snapshot pejabat penerbit SIP Kendaraan dari konfigurasi Master Unit Kerja.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Timpa snapshot yang sudah ada.')

    def handle(self, *args, **options):
        force = options.get('force')
        updated = 0
        skipped = 0

        qs = SIPKendaraan.objects.select_related(
            'kendaraan__unit_kerja',
            'pegawai__unit_kerja',
            'pejabat_penerbit_sip_kendaraan',
        )

        for sip in qs.iterator():
            before = (
                sip.pejabat_penerbit_sip_kendaraan_id,
                sip.nama_pejabat_penerbit_sip_kendaraan,
                sip.nip_pejabat_penerbit_sip_kendaraan,
                sip.jabatan_pejabat_penerbit_sip_kendaraan,
                sip.pejabat_penandatangan,
            )
            apply_snapshot_penerbit_sip_kendaraan(sip, force=force)
            after = (
                sip.pejabat_penerbit_sip_kendaraan_id,
                sip.nama_pejabat_penerbit_sip_kendaraan,
                sip.nip_pejabat_penerbit_sip_kendaraan,
                sip.jabatan_pejabat_penerbit_sip_kendaraan,
                sip.pejabat_penandatangan,
            )
            if before != after:
                sip.save(update_fields=[
                    'pejabat_penerbit_sip_kendaraan',
                    'nama_pejabat_penerbit_sip_kendaraan',
                    'nip_pejabat_penerbit_sip_kendaraan',
                    'jabatan_pejabat_penerbit_sip_kendaraan',
                    'pejabat_penandatangan',
                    'updated_at',
                ])
                updated += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f'Selesai. Diupdate: {updated}, dilewati: {skipped}'))
