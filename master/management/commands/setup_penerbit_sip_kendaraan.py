from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from master.models import UnitKerja, Pegawai


def norm(v):
    return (v or '').upper()


class Command(BaseCommand):
    help = 'Mengisi jenis unit kerja dan kandidat jabatan penerbit SIP Kendaraan berdasarkan nama unit.'

    def handle(self, *args, **options):
        for group_name in ['Pejabat Penerbit SIP', 'Sekretaris Ditjen', 'Sekretaris Eselon I', 'Kepala Sentra', 'Kepala Balai', 'Kepala Biro Umum']:
            Group.objects.get_or_create(name=group_name)
        updated = 0
        for unit in UnitKerja.objects.all():
            name = norm(unit.nama_unit)
            if 'BIRO UMUM' in name:
                unit.jenis_unit = 'BIRO_UMUM'; jabatan = 'Kepala Biro Umum'
            elif 'DIREKTORAT JENDERAL' in name or 'DITJEN' in name:
                unit.jenis_unit = 'DITJEN'; jabatan = f'Sekretaris {unit.nama_unit}'
            elif 'INSPEKTORAT JENDERAL' in name or 'ITJEN' in name:
                unit.jenis_unit = 'ITJEN'; jabatan = f'Sekretaris {unit.nama_unit}'
            elif 'SENTRA' in name:
                unit.jenis_unit = 'SENTRA'; jabatan = f'Kepala {unit.nama_unit}'
            elif 'BALAI' in name:
                unit.jenis_unit = 'BALAI'; jabatan = f'Kepala {unit.nama_unit}'
            elif 'PUSAT' in name:
                unit.jenis_unit = 'PUSAT'; jabatan = f'Kepala {unit.nama_unit}'
            else:
                jabatan = unit.nama_jabatan_penerbit_sip_kendaraan or 'Pejabat Penerbit SIP Kendaraan'
            if not unit.nama_jabatan_penerbit_sip_kendaraan:
                unit.nama_jabatan_penerbit_sip_kendaraan = jabatan
            if not unit.pejabat_penerbit_sip_kendaraan_id:
                keyword = 'Kepala Biro Umum' if unit.jenis_unit == 'BIRO_UMUM' else ('Sekretaris' if unit.jenis_unit in ['DITJEN','ITJEN','BADAN'] else 'Kepala')
                pegawai = Pegawai.objects.filter(unit_kerja=unit, jabatan__icontains=keyword, status_pegawai__iexact='Aktif').first() or Pegawai.objects.filter(unit_kerja=unit, jabatan__icontains=keyword).first()
                if pegawai:
                    unit.pejabat_penerbit_sip_kendaraan = pegawai
            unit.save()
            updated += 1
        self.stdout.write(self.style.SUCCESS(f'Selesai update {updated} unit kerja dan membuat grup penerbit SIP.'))
