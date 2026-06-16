import os
import re
from html import escape
from io import BytesIO
from decimal import Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Image as PlatypusImage
)
from master.models import Pegawai

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
except Exception:  # pragma: no cover
    svg2rlg = None
    renderPDF = None

BULAN_ID = [
    '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]


def tanggal_id(value):
    if not value:
        return '-'
    return f'{value.day} {BULAN_ID[value.month]} {value.year}'


def rupiah(value):
    if value in [None, '']:
        return '-'
    try:
        n = Decimal(str(value))
        return 'Rp ' + f'{int(n):,}'.replace(',', '.')
    except Exception:
        return str(value)


def safe(value, default='-'):
    if value in [None, '']:
        return default
    return str(value)


def pdf_text(value, default='-'):
    """Teks aman untuk ReportLab Paragraph agar karakter &, <, > tidak merusak layout PDF."""
    return escape(safe(value, default)).replace('\n', '<br/>')


def filename_safe(text):
    text = re.sub(r'[^A-Za-z0-9_.-]+', '_', str(text or 'dokumen'))
    return text.strip('_') or 'dokumen'




def _file_path_from_field(file_field):
    if not file_field:
        return None
    try:
        path = file_field.path
        if path and os.path.exists(path):
            return path
    except Exception:
        return None
    return None


def _image_or_placeholder(file_field, label, width=2.65 * cm, height=3.25 * cm):
    """Buat blok foto untuk PDF; jika file kosong tampilkan kotak placeholder."""
    path = _file_path_from_field(file_field)
    if path:
        try:
            img = PlatypusImage(path, width=width, height=height, kind='proportional')
            img.hAlign = 'CENTER'
            return img
        except Exception:
            pass
    t = Table([[Paragraph(pdf_text(label), _styles()['CenterSmall'])]], colWidths=[width], rowHeights=[height])
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
    ]))
    return t


def _emeterai_tte_box(styles, label='e-Meterai Elektronik'):
    data = [[
        Paragraph(f'<b>{pdf_text(label)}</b><br/><font size=7>Area pembubuhan meterai elektronik</font>', styles['CenterSmall'])
    ]]
    t = Table(data, colWidths=[3.2 * cm], rowHeights=[2.35 * cm])
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.6, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return t


def _sip_rumah_surat_pernyataan(styles, sip):
    """Lampiran Surat Pernyataan sesuai contoh SIP Rumah Negara.

    Lampiran ini disiapkan sebagai konsep untuk dibubuhi e-Meterai dan TTE
    oleh calon pengguna/pemegang SIP melalui alur aplikasi.
    """
    story = []
    story.append(PageBreak())
    story.append(Paragraph('<u>SURAT PERNYATAAN</u>', styles['TitleDoc']))
    story.append(Spacer(1, 0.55 * cm))

    p = sip.pegawai
    r = sip.rumah_dinas
    unit = getattr(getattr(p, 'unit_kerja', None), 'nama_unit', '-')
    data_p = [
        [Paragraph('Yang bertanda tangan di bawah ini:', styles['Body']), ''],
        [Paragraph('Nama', styles['Body']), Paragraph(f': {pdf_text(getattr(p, "nama", "-"))}', styles['Body'])],
        [Paragraph('NIP', styles['Body']), Paragraph(f': {pdf_text(getattr(p, "nip", "-"))}', styles['Body'])],
        [Paragraph('Jabatan', styles['Body']), Paragraph(f': {pdf_text(getattr(p, "jabatan", "-"))}', styles['Body'])],
        [Paragraph('Unit Organisasi', styles['Body']), Paragraph(f': {pdf_text(unit)}', styles['Body'])],
    ]
    t = Table(data_p, colWidths=[3.4 * cm, 13.0 * cm])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    story.append(t)
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        f'Sesuai dengan Surat Izin Penghunian Rumah Negara Nomor: <b>{pdf_text(sip.nomor_sip)}</b> tanggal {tanggal_id(getattr(sip, "tanggal_sip", None))}.',
        styles['Body']
    ))
    story.append(Spacer(1, 0.18 * cm))
    story.append(Paragraph('Dengan ini saya menyatakan sebagai berikut:', styles['Body']))
    statements = [
        f'Menempati Rumah Negara di {safe(getattr(r, "alamat", "-"))} dan tidak akan mengalihkan hak penempatan Rumah Negara kepada siapapun.',
        'Memelihara dan merawat Rumah Negara dengan sebaik-baiknya.',
        'Membayar sewa Rumah Negara sesuai ketentuan yang ditetapkan.',
        'Tidak akan menambah, mengubah, atau merombak Rumah Negara tanpa persetujuan pejabat yang berwenang.',
        'Tidak akan menggunakan Rumah Negara untuk keperluan lain selain rumah tinggal keluarga.',
        'Menanggung biaya penggunaan fasilitas Rumah Negara, antara lain listrik, telepon, air, pajak bumi dan bangunan, serta biaya lain sesuai ketentuan.',
        'Bersedia meninggalkan atau mengosongkan Rumah Negara dalam waktu paling lambat 3 (tiga) bulan setelah tidak memangku jabatan, pensiun, atau dimutasi keluar kota Jakarta tanpa menuntut biaya ganti rugi.',
        'Bersedia dikenakan sanksi dan/atau dikosongkan secara paksa apabila melanggar ketentuan penghunian Rumah Negara.',
        'Bersedia dituntut di muka pengadilan secara perdata maupun pidana apabila melanggar ketentuan pernyataan ini.',
    ]
    for i, text in enumerate(statements, 1):
        story.append(Paragraph(f'{i}. {pdf_text(text)}', styles['BodySmall']))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        'Pernyataan ini saya buat dengan sebenarnya tanpa paksaan dari pihak manapun dan bersedia menerima sanksi apabila melanggar pernyataan yang saya buat.',
        styles['Body']
    ))
    story.append(Spacer(1, 0.45 * cm))

    name = safe(getattr(p, 'nama', '-'))
    nip = safe(getattr(p, 'nip', '-'))
    sign_table = Table(
        [[
            '',
            Paragraph(f'Jakarta, {tanggal_id(getattr(sip, "tanggal_sip", None))}<br/>Yang membuat pernyataan', styles['Body'])
        ], [
            '',
            _emeterai_tte_box(styles)
        ], [
            '',
            Paragraph(f'<b>{pdf_text(name)}</b><br/>NIP. {pdf_text(nip)}<br/><font size=7>(TTE BSrE calon pengguna rumah)</font>', styles['Body'])
        ]],
        colWidths=[8.7 * cm, 7.7 * cm]
    )
    sign_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (1, 0), (1, -1), 'CENTER')]))
    story.append(sign_table)
    return story


def _sip_rumah_lampiran_foto(styles, sip):
    story = []
    r = sip.rumah_dinas
    story.append(PageBreak())
    story.append(Paragraph('<u>LAMPIRAN FOTO RUMAH NEGARA</u>', styles['TitleDoc']))
    story.append(Spacer(1, 0.25 * cm))
    info = Table([
        [Paragraph('Nomor SIP', styles['KeyCell']), Paragraph(f': {pdf_text(sip.nomor_sip)}', styles['ValueCell'])],
        [Paragraph('Alamat Rumah Negara', styles['KeyCell']), Paragraph(f': {pdf_text(getattr(r, "alamat", "-"))}', styles['ValueCell'])],
        [Paragraph('Nama Rumah', styles['KeyCell']), Paragraph(f': {pdf_text(getattr(r, "nama_rumah", "-"))}', styles['ValueCell'])],
    ], colWidths=[4.0 * cm, 12.4 * cm])
    story.append(info)
    story.append(Spacer(1, 0.35 * cm))
    foto_depan = getattr(r, 'foto_depan', None)
    foto_utama = _image_or_placeholder(foto_depan, 'Foto Rumah Negara', width=8.2 * cm, height=5.6 * cm)
    foto_utama.hAlign = 'CENTER' if hasattr(foto_utama, 'hAlign') else None
    story.append(foto_utama)
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph('Foto rumah negara digunakan sebagai lampiran konsep SIP. Jika foto belum tersedia pada master rumah negara, unggah foto melalui Master Rumah Negara.', styles['BodySmall']))
    return story


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterSmall', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, leading=10))
    styles.add(ParagraphStyle(name='HeaderTitle', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=13, leading=15))
    styles.add(ParagraphStyle(name='HeaderSub', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=13))
    styles.add(ParagraphStyle(name='TitleDoc', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=10, leading=12, underlineWidth=1))
    styles.add(ParagraphStyle(name='Body', parent=styles['Normal'], alignment=TA_LEFT, fontSize=8.5, leading=11))
    styles.add(ParagraphStyle(name='BodySmall', parent=styles['Normal'], alignment=TA_LEFT, fontSize=7.5, leading=9))
    styles.add(ParagraphStyle(name='TableTiny', parent=styles['Normal'], alignment=TA_CENTER, fontSize=6.4, leading=7.6, wordWrap='CJK'))
    styles.add(ParagraphStyle(name='TableTinyLeft', parent=styles['Normal'], alignment=TA_LEFT, fontSize=6.6, leading=8, wordWrap='CJK'))
    styles.add(ParagraphStyle(name='TableHeaderTiny', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=6.8, leading=8, wordWrap='CJK'))
    styles.add(ParagraphStyle(name='KeyCell', parent=styles['Normal'], alignment=TA_LEFT, fontSize=7.4, leading=8.8, wordWrap='CJK'))
    styles.add(ParagraphStyle(name='ValueCell', parent=styles['Normal'], alignment=TA_LEFT, fontSize=7.4, leading=8.8, wordWrap='CJK'))
    styles.add(ParagraphStyle(name='Watermark', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#c53030')))
    return styles


def _logo_drawing(width=2.2 * cm, height=1.9 * cm):
    logo_path = os.path.join(settings.BASE_DIR, 'logo-kemensos.svg')
    if svg2rlg and os.path.exists(logo_path):
        try:
            drawing = svg2rlg(logo_path)
            if drawing.width and drawing.height:
                scale = min(width / drawing.width, height / drawing.height)
                drawing.scale(scale, scale)
                drawing.width *= scale
                drawing.height *= scale
            return drawing
        except Exception:
            return ''
    return ''


def _header(styles):
    logo = _logo_drawing()
    text = [
        Paragraph('KEMENTERIAN SOSIAL REPUBLIK INDONESIA', styles['HeaderTitle']),
        Paragraph('SEKRETARIAT JENDERAL', styles['HeaderSub']),
        Paragraph('BIRO UMUM', styles['HeaderSub']),
        Paragraph('JALAN SALEMBA RAYA NOMOR 28 JAKARTA PUSAT TELEPON: 021 - 3103591 LAMAN: https://www.kemensos.go.id', styles['CenterSmall']),
    ]
    t = Table([[logo, text]], colWidths=[2.7 * cm, 14.2 * cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    line = Table([['']], colWidths=[17 * cm], rowHeights=[0.08 * cm])
    line.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.black)]))
    return [t, line, Spacer(1, 0.22 * cm)]


def _watermark_story(story, styles, is_concept, signer_title='SEKRETARIS JENDERAL'):
    # Sesuai alur proses bisnis terakhir, PDF hasil generate tidak lagi diberi
    # watermark konsep/draft dihilangkan dari dokumen PDF. Status proses
    # cukup dikendalikan oleh status transaksi di aplikasi.
    return


def _pegawai_penandatangan(jabatan_keyword, fallback_nama='-', fallback_nip='-'):
    """Ambil pejabat penandatangan dari Master Pegawai berdasarkan jabatan.

    Contoh: SIP Kendaraan mengambil pegawai dengan jabatan Kepala Biro Umum,
    sedangkan SIP Rumah Negara mengambil pegawai dengan jabatan Sekretaris Jenderal.
    """
    try:
        pegawai = (
            Pegawai.objects
            .filter(jabatan__icontains=jabatan_keyword, status_pegawai__iexact='Aktif')
            .order_by('nama')
            .first()
        ) or (
            Pegawai.objects
            .filter(jabatan__icontains=jabatan_keyword)
            .order_by('nama')
            .first()
        )
        if pegawai:
            return pegawai.nama, pegawai.nip
    except Exception:
        pass
    return fallback_nama, fallback_nip



def _sip_signer_from_snapshot(sip, default_title):
    title = getattr(sip, 'jabatan_pejabat_penerbit_sip_kendaraan', None) or getattr(sip, 'pejabat_penandatangan', None) or default_title
    name = getattr(sip, 'nama_pejabat_penerbit_sip_kendaraan', None) or ''
    nip = getattr(sip, 'nip_pejabat_penerbit_sip_kendaraan', None) or ''
    pegawai = getattr(sip, 'pejabat_penerbit_sip_kendaraan', None)
    if pegawai:
        name = name or getattr(pegawai, 'nama', '')
        nip = nip or getattr(pegawai, 'nip', '')
        title = title or getattr(pegawai, 'jabatan', '')
    return title or default_title, name or '-', nip or '-'

def _approval_box(styles, sip, approved=False, signer_title='SEKRETARIS JENDERAL'):
    """Blok tanda tangan dua kolom yang rapi dan sejajar.

    Nama dan NIP pihak kiri serta pejabat kanan berada pada baris yang sama,
    sehingga tidak turun/naik walaupun blok tanggal dan jabatan di kanan lebih panjang.
    Semua tanda tangan diarahkan untuk TTE BSrE.
    """
    signer_title_upper = safe(signer_title).upper()

    # Untuk SIP Kendaraan, pejabat penerbit diambil dari snapshot unit kerja.
    if hasattr(sip, 'jabatan_pejabat_penerbit_sip_kendaraan'):
        snapshot_title, snapshot_name, snapshot_nip = _sip_signer_from_snapshot(sip, signer_title)
        signer_title_upper = safe(snapshot_title).upper()
        signer_name, signer_nip = snapshot_name, snapshot_nip
    elif 'KEPALA BIRO UMUM' in signer_title_upper:
        signer_name, signer_nip = _pegawai_penandatangan(
            'Kepala Biro Umum',
            fallback_nama='ROBBEN RICO',
            fallback_nip='19800913 200212 1 001',
        )
    elif 'SEKRETARIS JENDERAL' in signer_title_upper:
        signer_name, signer_nip = _pegawai_penandatangan(
            'Sekretaris Jenderal',
            fallback_nama='ROBBEN RICO',
            fallback_nip='19800913 200212 1 001',
        )
    else:
        signer_name, signer_nip = _pegawai_penandatangan(signer_title, fallback_nama='-', fallback_nip='-')

    left_title = safe(getattr(sip.pegawai, 'jabatan', '') or 'Pemegang SIP')
    left_name = safe(getattr(sip.pegawai, 'nama', '-'))
    left_nip = safe(getattr(sip.pegawai, 'nip', '-'))

    right_title = signer_title_upper
    if approved:
        right_title = f'{right_title}<br/><font size=7>(TTE BSrE)</font>'

    data = [
        [
            Paragraph(f'{pdf_text(left_title)}<br/><font size=7>(TTE BSrE)</font>', styles['Body']),
            Paragraph(f'Ditetapkan di&nbsp;&nbsp;: Jakarta<br/>Pada Tanggal&nbsp;: {tanggal_id(getattr(sip, "tanggal_sip", None))}', styles['Body']),
        ],
        ['', Paragraph(right_title, styles['Body'])],
        ['', ''],
        [Paragraph(f'<b>{pdf_text(left_name)}</b>', styles['Body']), Paragraph(f'<b>{pdf_text(signer_name)}</b>', styles['Body'])],
        [Paragraph(f'NIP. {pdf_text(left_nip)}', styles['Body']), Paragraph(f'NIP. {pdf_text(signer_nip)}', styles['Body'])],
    ]
    t = Table(
        data,
        colWidths=[8.2 * cm, 8.2 * cm],
        rowHeights=[None, None, 1.55 * cm, None, None],
    )
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return t


def generate_sip_kendaraan_pdf(sip, concept=True, save_to_model=True):
    styles = _styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.6 * cm, leftMargin=1.6 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    story = []
    story.extend(_header(styles))
    signer_title, _, _ = _sip_signer_from_snapshot(sip, 'Pejabat Penerbit SIP Kendaraan')
    _watermark_story(story, styles, concept, signer_title=signer_title)

    story.append(Paragraph('<u>SURAT IZIN PENUNJUKAN PEMAKAI KENDARAAN DINAS RODA EMPAT</u>', styles['TitleDoc']))
    story.append(Paragraph(f'Nomor : {safe(sip.nomor_sip)}', styles['CenterSmall']))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph('Dengan ini memberikan izin pemakaian Kendaraan Dinas Roda 4 (empat), dengan spesifikasi tersebut di bawah ini:', styles['Body']))
    story.append(Spacer(1, 0.12 * cm))

    k = sip.kendaraan

    def tc(value):
        return Paragraph(safe(value), styles['TableTiny'])

    def tl(value):
        return Paragraph(safe(value), styles['TableTinyLeft'])

    data = [
        [tc('NO.'), tc('KODE BARANG'), tc('NUP'), tc('JENIS KENDARAAN'), tc('MERK/TIPE'), tc('NO. RANGKA'), tc('NO. MESIN'), tc('NO. POLISI'), tc('TAHUN')],
        [
            tc('1'),
            tc(getattr(k, 'kode_barang', '')),
            tc(getattr(k, 'nup', '')),
            tc(getattr(k, 'jenis_kendaraan', '')),
            tl(f"{safe(getattr(k, 'merek', ''))} {safe(getattr(k, 'tipe', ''), '')}"),
            tc(getattr(k, 'nomor_rangka', '')),
            tc(getattr(k, 'nomor_mesin', '')),
            tc(getattr(k, 'nomor_polisi', '')),
            tc(getattr(k, 'tahun_perolehan', '')),
        ],
        [tc('2'), tl('Kunci Kendaraan'), '', '', '', '', '', '', ''],
        [tc('3'), tl('STNK dan Surat Pajak Kendaraan'), '', '', '', '', '', '', ''],
    ]
    table = Table(
        data,
        colWidths=[0.65*cm, 1.9*cm, 0.75*cm, 2.0*cm, 3.0*cm, 2.25*cm, 2.05*cm, 1.65*cm, 0.9*cm],
        repeatRows=1,
    )
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('SPAN', (1,2), (-1,2)),
        ('SPAN', (1,3), (-1,3)),
        ('ALIGN', (1,2), (-1,3), 'LEFT'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.22 * cm))

    p = sip.pegawai
    unit = getattr(getattr(p, 'unit_kerja', None), 'nama_unit', '-')
    pegawai_table = Table([
        ['KEPADA', ''],
        ['Nama', f': {safe(p.nama)}'],
        ['NIP', f': {safe(p.nip)}'],
        ['Jabatan', f': {safe(p.jabatan)}'],
        ['Unit Kerja', f': {safe(unit)}'],
        ['Keterangan', f': {safe(sip.tujuan_pemakaian or sip.lokasi_penggunaan)}'],
        ['Masa Berlaku SIP', f': {safe(getattr(sip, "masa_berlaku_display", "-"))}'],
    ], colWidths=[4.2*cm, 12.2*cm])
    pegawai_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(pegawai_table)
    story.append(Spacer(1, 0.18 * cm))

    ketentuan = [
        'Pemegang Kendaraan Dinas bertanggung jawab penuh atas keselamatan dan keamanan kendaraan yang dipercayakan untuk dipergunakan dalam rangka kelancaran tugas dinas di lingkungan Kementerian Sosial RI.',
        'Biaya BBM, pemeliharaan dan perbaikan Kendaraan Dinas ditanggung sesuai ketentuan unit kerja/satker pemilik kendaraan. Kerusakan maupun kehilangan Kendaraan Dinas tersebut atau bagian-bagiannya serta biaya-biaya lainnya akibat kelalaian adalah menjadi tanggung jawab yang bersangkutan.',
        f'Mutasi Kendaraan Dinas kepada pegawai lain harus mendapat persetujuan {safe(signer_title)}.',
        f'Apabila pemegang Kendaraan Dinas dimutasikan, maka Kendaraan Dinas tersebut diserahkan kembali kepada unit kerja/satker pemilik kendaraan atau {safe(signer_title)} sesuai kewenangan.',
        f'Kendaraan Dinas dapat ditarik/dicabut tanpa menuntut ganti rugi apapun apabila {safe(signer_title)} memandang perlu, pemakai berhenti sebagai pejabat, pensiun/meninggal, atau dimutasikan/dipindahkan tugas.',
    ]
    story.append(Paragraph('Dengan ketentuan sebagai berikut:', styles['Body']))
    for i, text in enumerate(ketentuan, 1):
        story.append(Paragraph(f'{i}. {text}', styles['BodySmall']))
    story.append(Spacer(1, 0.12 * cm))
    story.append(Paragraph('Demikian Surat Izin Penunjukan Pemakai Kendaraan Dinas ini dibuat untuk dapat dipergunakan sebagaimana mestinya.', styles['Body']))
    story.append(Spacer(1, 0.22 * cm))
    story.append(_approval_box(styles, sip, approved=not concept, signer_title=signer_title))
    doc.build(story)
    content = buffer.getvalue()
    buffer.close()

    if save_to_model:
        field = 'file_konsep_pdf' if concept else 'file_final_pdf'
        filename = f"SIP_Kendaraan_{filename_safe(sip.nomor_sip)}_{'konsep' if concept else 'final'}.pdf"
        getattr(sip, field).save(filename, ContentFile(content), save=False)
        if not concept:
            sip.status = 'MENUNGGU_TTE'
            if hasattr(sip, 'status_tte'):
                sip.status_tte = 'SIAP_TTE'
        sip.save()
    return content


def generate_sip_rumah_pdf(sip, concept=True, save_to_model=True):
    styles = _styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )
    story = []
    story.extend(_header(styles))
    _watermark_story(story, styles, concept, signer_title='SEKRETARIS JENDERAL')

    story.append(Paragraph('<u>SURAT IZIN PENGHUNIAN RUMAH NEGARA</u>', styles['TitleDoc']))
    story.append(Paragraph(f'Nomor : {pdf_text(sip.nomor_sip)}', styles['CenterSmall']))
    story.append(Spacer(1, 0.18 * cm))

    dasar = sip.dasar_penerbitan or (
        '1. Peraturan Pemerintah Republik Indonesia Nomor 21 Tahun 2023 tentang Jenis dan Tarif atas Jenis PNBP;\n'
        '2. Keputusan Menteri Permukiman dan Prasarana Wilayah Nomor 373/KPTS/M/2001 tentang Sewa Rumah Negara;\n'
        '3. Surat Edaran Direktur Jenderal Anggaran Nomor SE-22/A/2002 tentang Sewa Rumah Negara;\n'
        '4. Ketentuan penggunaan Rumah Jabatan di lingkungan Kementerian Sosial RI.'
    )
    story.append(Paragraph('<b>Dasar:</b>', styles['Body']))
    for line in str(dasar).split('\n'):
        story.append(Paragraph(pdf_text(line), styles['BodySmall']))
    story.append(Spacer(1, 0.15 * cm))

    def kc(value):
        return Paragraph(pdf_text(value), styles['KeyCell'])

    def vc(value):
        return Paragraph(pdf_text(value), styles['ValueCell'])

    def tc(value):
        return Paragraph(pdf_text(value), styles['TableTiny'])

    def th(value):
        return Paragraph(pdf_text(value), styles['TableHeaderTiny'])

    p = sip.pegawai
    unit = getattr(getattr(p, 'unit_kerja', None), 'nama_unit', '-')
    data_p = [
        [Paragraph('<b>1. Diberikan kepada</b>', styles['KeyCell']), ''],
        [kc('Nama'), vc(f': {safe(p.nama)}')],
        [kc('NIP'), vc(f': {safe(p.nip)}')],
        [kc('Jabatan'), vc(f': {safe(p.jabatan)}')],
        [kc('Unit Organisasi'), vc(f': {safe(unit)}')],
    ]
    pegawai_table = Table(data_p, colWidths=[4.2 * cm, 12.2 * cm], hAlign='LEFT')
    pegawai_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(pegawai_table)
    story.append(Spacer(1, 0.12 * cm))

    story.append(Paragraph('Beserta dengan keluarga yang terdiri:', styles['BodySmall']))
    fam = Table(
        [
            [th('NO.'), th('NAMA KELUARGA'), th('JENIS KELAMIN'), th('UMUR'), th('HUBUNGAN KELUARGA')],
            [tc('1'), tc(''), tc(''), tc(''), tc('')],
        ],
        colWidths=[0.9 * cm, 6.2 * cm, 3.0 * cm, 2.0 * cm, 4.3 * cm],
        repeatRows=1,
        hAlign='LEFT',
    )
    fam.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(fam)
    story.append(Spacer(1, 0.15 * cm))

    r = sip.rumah_dinas
    rumah_data = [
        [Paragraph('<b>2. Keterangan mengenai rumah:</b>', styles['KeyCell']), ''],
        [kc('Alamat Rumah Negara'), vc(f': {safe(r.alamat)}')],
        [kc('Luas tanah'), vc(f': {safe(r.luas_tanah)} m2')],
        [kc('Luas bangunan'), vc(f': {safe(r.luas_bangunan)} m2')],
        [kc('Dibangun tahun'), vc(f': {safe(r.tahun_dibangun)}')],
        [kc('Besaran sewa'), vc(f': {rupiah(sip.nilai_pnbp)} / Bulan')],
        [kc('Golongan/Jenis Rumah Negara'), vc(f': {safe(r.jenis_rumah)}')],
        [kc('Masa Berlaku SIP'), vc(f': {safe(getattr(sip, "masa_berlaku_display", "-"))}')],
    ]
    rumah_table = Table(rumah_data, colWidths=[4.4 * cm, 12.0 * cm], hAlign='LEFT')
    rumah_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(rumah_table)
    story.append(Spacer(1, 0.15 * cm))

    ketentuan = [
        'Ketentuan Penghunian Rumah Negara tersebut sebagaimana tercantum dalam lampiran Surat Keputusan ini.',
        f'Surat Izin ini berlaku: {safe(getattr(sip, "masa_berlaku_display", "-") )}.',
        'Surat Izin Penghunian Rumah Negara ini dapat diubah jika ternyata ada kekeliruan atau kesalahan.',
        'Penghuni wajib memelihara rumah negara dengan sebaik-baiknya, membayar sewa sesuai ketentuan, dan tidak mengalihkan hak penghuniannya kepada pihak lain.',
    ]
    story.append(Paragraph('3. Ketentuan Penghunian Rumah Negara:', styles['Body']))
    for i, text in enumerate(ketentuan, 1):
        story.append(Paragraph(f'{chr(96+i)}. {pdf_text(text)}', styles['BodySmall']))
    story.append(Spacer(1, 0.12 * cm))
    story.append(Paragraph('Surat Izin Penghunian Rumah Negara diberikan untuk dipergunakan sebagaimana mestinya.', styles['Body']))
    story.append(Spacer(1, 0.16 * cm))

    # Foto calon pengguna/pemegang SIP ditampilkan pada konsep, mengikuti
    # contoh dokumen SIP Rumah Negara yang memuat foto pemegang SIP.
    foto_pemegang = _image_or_placeholder(getattr(p, 'foto', None), 'Foto Pemegang SIP', width=2.45 * cm, height=3.0 * cm)
    sign_area = Table([[foto_pemegang, _approval_box(styles, sip, approved=not concept, signer_title='SEKRETARIS JENDERAL')]], colWidths=[3.1 * cm, 13.2 * cm])
    sign_area.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(sign_area)
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph('<b>Tembusan disampaikan kepada Yth.:</b><br/>1. Menteri Sosial sebagai laporan<br/>2. Inspektur Jenderal Kementerian Sosial RI<br/>3. Kepala Biro Keuangan Kementerian Sosial RI<br/>4. Kepala Biro Umum Kementerian Sosial RI', styles['BodySmall']))

    # Lampiran yang diminta: Surat Pernyataan dengan area e-Meterai
    # elektronik dan TTE, serta lampiran foto rumah negara.
    story.extend(_sip_rumah_surat_pernyataan(styles, sip))
    story.extend(_sip_rumah_lampiran_foto(styles, sip))

    doc.build(story)
    content = buffer.getvalue()
    buffer.close()

    if save_to_model:
        field = 'file_konsep_pdf' if concept else 'file_final_pdf'
        filename = f"SIP_Rumah_Negara_{filename_safe(sip.nomor_sip)}_{'konsep' if concept else 'final'}.pdf"
        getattr(sip, field).save(filename, ContentFile(content), save=False)
        if not concept:
            sip.status = 'MENUNGGU_TTE'
            if hasattr(sip, 'status_tte'):
                sip.status_tte = 'SIAP_TTE'
        sip.save()
    return content
