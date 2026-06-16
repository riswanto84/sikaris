KONDISI_ASET = [
    ('BAIK', 'Baik'),
    ('RUSAK_RINGAN', 'Rusak Ringan'),
    ('RUSAK_BERAT', 'Rusak Berat'),
]

STATUS_SIP = [
    ('DRAFT', 'Draft/Konsep'),
    ('DIAJUKAN', 'Diajukan'),
    ('DISETUJUI', 'Disetujui'),
    ('DITOLAK', 'Ditolak'),
    ('TERBIT', 'Terbit'),
    ('MENUNGGU_TTE', 'Menunggu TTE BSrE'),
    ('BERAKHIR', 'Berakhir'),
    ('DIBATALKAN', 'Dibatalkan'),
]


STATUS_PEMANFAATAN_KENDARAAN = [
    ('TERSEDIA', 'Tersedia'),
    ('DIGUNAKAN', 'Digunakan'),
    ('DALAM_SERVICE', 'Dalam Service'),
    ('TIDAK_AKTIF', 'Tidak Aktif'),
    ('TIDAK_DIKETAHUI', 'Tidak Diketahui Keberadaannya'),
    ('DIKUASAI_PIHAK_LAIN', 'Dikuasai Pihak Lain'),
]

STATUS_PEMANFAATAN_RUMAH = [
    ('KOSONG', 'Kosong'),
    ('DIHUNI', 'Dihuni'),
    ('DALAM_PERBAIKAN', 'Dalam Perbaikan'),
    ('TIDAK_AKTIF', 'Tidak Aktif'),
    ('DALAM_PENGUASAAN_PIHAK_LAIN', 'Dalam Penguasaan Pihak Lain'),
]


JENIS_KENDARAAN_CHOICES = [
    ('MOBIL', 'Mobil'),
    ('SEPEDA_MOTOR', 'Sepeda Motor'),
    ('MOTOR_RODA_3', 'Motor Roda 3'),
    ('KENDARAAN_LAINNYA', 'Kendaraan Lainnya'),
    ('OPERASIONAL', 'Operasional'),
    ('DINAS_JABATAN', 'Dinas Jabatan'),
    ('KENDARAAN_SEWA', 'Kendaraan Sewa'),
]


JENIS_UNIT_KERJA_CHOICES = [
    ('BIRO_UMUM', 'Biro Umum'),
    ('DITJEN', 'Direktorat Jenderal / Sekretariat Ditjen'),
    ('ITJEN', 'Inspektorat Jenderal / Sekretariat Itjen'),
    ('BADAN', 'Badan'),
    ('PUSAT', 'Pusat'),
    ('SENTRA', 'Sentra'),
    ('BALAI', 'Balai'),
    ('LAINNYA', 'Lainnya'),
]

STATUS_TTE_DOKUMEN = [
    ('BELUM', 'Belum TTE'),
    ('SIAP_TTE', 'Siap TTE'),
    ('PROSES_TTE', 'Proses TTE'),
    ('SUDAH_TTE', 'Sudah TTE'),
    ('DITOLAK_TTE', 'Ditolak TTE'),
]
