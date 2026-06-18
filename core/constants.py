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


STATUS_PENGGUNAAN_KENDARAAN = [
    ('-', '-'),
    ('DIGUNAKAN_SENDIRI_DINAS_JABATAN', 'Digunakan sendiri untuk dinas jabatan'),
    ('DIGUNAKAN_SENDIRI_OPERASIONAL', 'Digunakan sendiri untuk operasional'),
    ('DIGUNAKAN_SATKER_LAIN_DALAM_KL', 'Digunakan oleh satker lain dalam satu Kementerian/ Lembaga (K/L)'),
    ('DIGUNAKAN_SATKER_LAIN_DILUAR_KL', 'Digunakan oleh satker lain diluar Kementerian/ Lembaga (K/L)'),
    ('DIGUNAKAN_PIHAK_LAIN_SESUAI_KETENTUAN', 'Digunakan Pihak Lain Sesuai Ketentuan'),
    ('BMN_TIDAK_DIGUNAKAN', 'BMN Tidak Digunakan'),
    ('DIGUNAKAN_PIHAK_LAIN', 'Digunakan Pihak Lain'),
    ('DIGUNAKAN_PIHAK_LAIN_TIDAK_SESUAI_PROSEDUR', 'Digunakan Pihak Lain Tidak Sesuai Prosedur'),
    ('DIGUNAKAN_SENDIRI_KENDARAAN_FUNGSIONAL', 'Digunakan sendiri untuk kendaraan fungsional'),
]

# Backward-compatible alias untuk kode lama yang masih mengimpor nama lama.
STATUS_PEMANFAATAN_KENDARAAN = STATUS_PENGGUNAAN_KENDARAAN

STATUS_PEMANFAATAN_RUMAH = [
    ('KOSONG', 'Kosong'),
    ('DIHUNI', 'Dihuni'),
    ('DALAM_PERBAIKAN', 'Dalam Perbaikan'),
    ('TIDAK_AKTIF', 'Tidak Aktif'),
    ('DALAM_PENGUASAAN_PIHAK_LAIN', 'Dalam Penguasaan Pihak Lain'),
]

STATUS_HUKUM_CHOICES = [
    ('TIDAK_ADA_SENGKETA', 'Tidak ada sengketa'),
    ('SENGKETA', 'Sengketa'),
]

JENIS_KENDARAAN_CHOICES = [
    ('ALAT_ANGKUTAN_APUNG_BERMOTOR_UNTUK_PENUMPANG_LAINNYA', 'Alat Angkutan Apung Bermotor Untuk Penumpang Lainnya'),
    ('ALAT_ANGKUTAN_DARAT_BERMOTOR_LAINNYA', 'Alat Angkutan Darat Bermotor Lainnya'),
    ('BUS_PENUMPANG_30_ORANG_KEATAS', 'Bus ( Penumpang 30 Orang Keatas )'),
    ('JEEP', 'Jeep'),
    ('KENDARAAN_BERMOTOR_RODA_TIGA_PENGANGKUT_BARANG', 'Kendaraan Bermotor Roda Tiga Pengangkut Barang'),
    ('KENDARAAN_DINAS_BERMOTOR_PERORANGAN_LAINNYA', 'Kendaraan Dinas Bermotor Perorangan Lainnya'),
    ('MICRO_BUS_PENUMPANG_15_S_D_29_ORANG', 'Micro Bus ( Penumpang 15 S/D 29 Orang )'),
    ('MINI_BUS_PENUMPANG_14_ORANG_KEBAWAH', 'Mini Bus ( Penumpang 14 Orang Kebawah )'),
    ('MOBIL_AMBULANCE', 'Mobil Ambulance'),
    ('MOBIL_JENAZAH', 'Mobil Jenazah'),
    ('MOBIL_LISTRIK', 'Mobil Listrik'),
    ('MOBIL_PATROLI', 'Mobil Patroli'),
    ('MOBIL_TANGKI_AIR', 'Mobil Tangki Air'),
    ('PESAWAT_TAK_BERAWAK', 'Pesawat tak berawak'),
    ('PICK_UP', 'Pick Up'),
    ('SEDAN', 'Sedan'),
    ('SEPEDA_MOTOR', 'Sepeda Motor'),
    ('STATION_WAGON', 'Station Wagon'),
    ('TRUCK_ATTACHMENT', 'Truck + Attachment'),
    ('KENDARAAN_LAINNYA', 'Kendaraan Lainnya'),
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
