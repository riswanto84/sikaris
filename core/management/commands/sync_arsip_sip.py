import csv
import re
import unicodedata
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from kendaraan.models import SIPKendaraan
from rumah_dinas.models import SIPRumahDinas


PLATE_RE = re.compile(r'\b([A-Z]{1,2})[\s\-]*(\d{1,4})[\s\-]*([A-Z]{1,4})\b', re.IGNORECASE)


def normalize_text(value):
    value = value or ''
    value = unicodedata.normalize('NFKD', str(value))
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r'[^A-Za-z0-9]+', ' ', value).strip().upper()
    return re.sub(r'\s+', ' ', value)


def normalize_plate(value):
    value = normalize_text(value)
    match = PLATE_RE.search(value)
    if not match:
        return ''
    return f'{match.group(1).upper()} {match.group(2)} {match.group(3).upper()}'


def extract_plates(text):
    results = []
    for match in PLATE_RE.finditer(text or ''):
        plate = f'{match.group(1).upper()} {match.group(2)} {match.group(3).upper()}'
        if plate not in results:
            results.append(plate)
    return results


def extract_name_from_rumah_filename(filename):
    stem = Path(filename).stem
    match = re.search(r'\(([^)]+)\)', stem)
    if match:
        return normalize_text(match.group(1))
    stem = re.sub(r'^\d{4}\s+\d+\s+', '', stem)
    stem = re.sub(r'SIP\s+RUMAH\s+DINAS', '', stem, flags=re.I)
    return normalize_text(stem)


class Command(BaseCommand):
    help = 'Menghubungkan dokumen arsip SIP Kendaraan dan SIP Rumah Negara dari folder media/arsip_sip ke data SIP yang sudah ada.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulasi saja, tidak menyimpan perubahan ke database.',
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Timpa dokumen_sip yang sudah ada. Default: tidak menimpa data yang sudah punya dokumen.',
        )
        parser.add_argument(
            '--base-dir',
            default='arsip_sip',
            help='Folder relatif di MEDIA_ROOT. Default: arsip_sip.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        replace = options['replace']
        base_dir = options['base_dir'].strip('/\\')
        media_root = Path(settings.MEDIA_ROOT)
        arsip_root = media_root / base_dir

        if not arsip_root.exists():
            self.stdout.write(self.style.ERROR(f'Folder arsip tidak ditemukan: {arsip_root}'))
            return

        report_rows = []
        kendaraan_attached = kendaraan_skipped = kendaraan_not_found = 0
        rumah_attached = rumah_skipped = rumah_not_found = 0

        kendaraan_root = arsip_root / 'kendaraan'
        if kendaraan_root.exists():
            for file_path in sorted(kendaraan_root.rglob('*.pdf')):
                rel_name = file_path.relative_to(media_root).as_posix()
                plates = extract_plates(file_path.name)
                if not plates:
                    kendaraan_not_found += 1
                    report_rows.append(['KENDARAAN', rel_name, '', '', 'TIDAK ADA NOMOR POLISI DI NAMA FILE'])
                    continue

                matched_any = False
                for plate in plates:
                    sip = (
                        SIPKendaraan.objects
                        .select_related('kendaraan')
                        .filter(kendaraan__nomor_polisi__iexact=plate)
                        .order_by('-tanggal_sip', '-id')
                        .first()
                    )
                    if not sip:
                        kendaraan_not_found += 1
                        report_rows.append(['KENDARAAN', rel_name, plate, '', 'TIDAK ADA DATA SIP/KENDARAAN YANG COCOK'])
                        continue

                    matched_any = True
                    if sip.dokumen_sip and not replace:
                        kendaraan_skipped += 1
                        report_rows.append(['KENDARAAN', rel_name, plate, sip.nomor_sip, 'SKIP: SIP SUDAH PUNYA DOKUMEN'])
                        continue

                    if not dry_run:
                        sip.dokumen_sip.name = rel_name
                        sip.save(update_fields=['dokumen_sip', 'updated_at'])
                    kendaraan_attached += 1
                    report_rows.append(['KENDARAAN', rel_name, plate, sip.nomor_sip, 'TERHUBUNG' if not dry_run else 'DRY RUN: AKAN DIHUBUNGKAN'])

                if not matched_any:
                    kendaraan_not_found += 1

        rumah_root = arsip_root / 'rumah_negara'
        if rumah_root.exists():
            for file_path in sorted(rumah_root.rglob('*.pdf')):
                rel_name = file_path.relative_to(media_root).as_posix()
                name_key = extract_name_from_rumah_filename(file_path.name)
                if not name_key:
                    rumah_not_found += 1
                    report_rows.append(['RUMAH_NEGARA', rel_name, '', '', 'TIDAK ADA NAMA PENGHUNI/PEMEGANG DI NAMA FILE'])
                    continue

                # Cari berdasarkan pemegang SIP atau penghuni aktual.
                # Dipilih latest karena satu pegawai bisa memiliki beberapa riwayat SIP.
                sip = None
                for candidate in SIPRumahDinas.objects.select_related('pegawai', 'penghuni').order_by('-tanggal_sip', '-id'):
                    pegawai_name = normalize_text(getattr(candidate.pegawai, 'nama', ''))
                    penghuni_name = normalize_text(getattr(candidate.penghuni, 'nama', '')) if candidate.penghuni_id else ''
                    if name_key and (name_key == pegawai_name or name_key == penghuni_name or name_key in pegawai_name or name_key in penghuni_name):
                        sip = candidate
                        break

                if not sip:
                    rumah_not_found += 1
                    report_rows.append(['RUMAH_NEGARA', rel_name, name_key, '', 'TIDAK ADA DATA SIP RUMAH YANG COCOK'])
                    continue

                if sip.dokumen_sip and not replace:
                    rumah_skipped += 1
                    report_rows.append(['RUMAH_NEGARA', rel_name, name_key, sip.nomor_sip, 'SKIP: SIP SUDAH PUNYA DOKUMEN'])
                    continue

                if not dry_run:
                    sip.dokumen_sip.name = rel_name
                    sip.save(update_fields=['dokumen_sip', 'updated_at'])
                rumah_attached += 1
                report_rows.append(['RUMAH_NEGARA', rel_name, name_key, sip.nomor_sip, 'TERHUBUNG' if not dry_run else 'DRY RUN: AKAN DIHUBUNGKAN'])

        report_path = media_root / base_dir / 'laporan_sync_arsip_sip.csv'
        if not dry_run:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with report_path.open('w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['jenis_arsip', 'file', 'kunci_pencarian', 'nomor_sip_terhubung', 'status'])
                writer.writerows(report_rows)

        self.stdout.write(self.style.SUCCESS('Sinkronisasi arsip SIP selesai.'))
        self.stdout.write(f'Kendaraan terhubung: {kendaraan_attached}, skip: {kendaraan_skipped}, tidak cocok: {kendaraan_not_found}')
        self.stdout.write(f'Rumah negara terhubung: {rumah_attached}, skip: {rumah_skipped}, tidak cocok: {rumah_not_found}')
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode dry-run: tidak ada data database yang diubah.'))
        else:
            self.stdout.write(f'Laporan hasil sinkronisasi: {report_path}')
