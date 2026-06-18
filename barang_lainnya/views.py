from io import BytesIO
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.roles import can_manage_sip, can_approve_sip_kendaraan, is_admin_system
from master.models import Pegawai

from .forms import SIPBarangLainnyaForm, SIPBarangLainnyaItemFormSet
from .models import SIPBarangLainnya


def _base_queryset(user):
    qs = SIPBarangLainnya.objects.select_related('pemegang_sip', 'pengguna_aktual', 'pejabat_penandatangan').prefetch_related('items')
    if is_admin_system(user):
        return qs
    try:
        pegawai = Pegawai.objects.filter(email=user.email).first() or Pegawai.objects.filter(nama__iexact=(user.get_full_name() or user.username)).first()
    except Exception:
        pegawai = None
    if can_approve_sip_kendaraan(user) and pegawai:
        return qs.filter(Q(dibuat_oleh=user) | Q(pejabat_penandatangan=pegawai))
    return qs.filter(Q(dibuat_oleh=user) | Q(pemegang_sip__email=user.email))


@login_required
def sip_list(request):
    qs = _base_queryset(request.user)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(nomor_sip__icontains=q) | Q(pemegang_sip__nama__icontains=q) | Q(items__nama_barang__icontains=q)).distinct()
    context = {
        'objects': qs,
        'page_title': 'SIP Barang Lainnya',
    }
    return render(request, 'barang_lainnya/sip_list.html', context)


@login_required
def sip_create(request):
    if not can_manage_sip(request.user):
        return HttpResponseForbidden('Tidak berwenang')
    if request.method == 'POST':
        form = SIPBarangLainnyaForm(request.POST, request.FILES, user=request.user)
        formset = SIPBarangLainnyaItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            obj = form.save(commit=False)
            obj.dibuat_oleh = request.user
            obj.status = 'DRAFT'
            obj.save()
            formset.instance = obj
            formset.save()
            messages.success(request, 'SIP Barang Lainnya berhasil disimpan.')
            return redirect('barang_lainnya:sip_detail', pk=obj.pk)
    else:
        form = SIPBarangLainnyaForm(user=request.user)
        formset = SIPBarangLainnyaItemFormSet(prefix='items')
    return render(request, 'barang_lainnya/sip_form.html', {'form': form, 'formset': formset, 'page_title': 'Form SIP Barang Lainnya', 'is_create': True})


@login_required
def sip_update(request, pk):
    obj = get_object_or_404(SIPBarangLainnya, pk=pk)
    if not (can_manage_sip(request.user) or is_admin_system(request.user)):
        return HttpResponseForbidden('Tidak berwenang')
    if request.method == 'POST':
        form = SIPBarangLainnyaForm(request.POST, request.FILES, instance=obj, user=request.user)
        formset = SIPBarangLainnyaItemFormSet(request.POST, instance=obj, prefix='items')
        if form.is_valid() and formset.is_valid():
            obj = form.save()
            formset.save()
            messages.success(request, 'SIP Barang Lainnya berhasil diperbarui.')
            return redirect('barang_lainnya:sip_detail', pk=obj.pk)
    else:
        form = SIPBarangLainnyaForm(instance=obj, user=request.user)
        formset = SIPBarangLainnyaItemFormSet(instance=obj, prefix='items')
    return render(request, 'barang_lainnya/sip_form.html', {'form': form, 'formset': formset, 'object': obj, 'page_title': 'Edit SIP Barang Lainnya', 'is_create': False})


@login_required
def sip_detail(request, pk):
    obj = get_object_or_404(SIPBarangLainnya.objects.select_related('pemegang_sip', 'pejabat_penandatangan').prefetch_related('items'), pk=pk)
    return render(request, 'barang_lainnya/sip_detail.html', {'object': obj, 'page_title': 'Detail SIP Barang Lainnya'})


@login_required
@require_POST
def sip_teruskan(request, pk):
    obj = get_object_or_404(SIPBarangLainnya, pk=pk)
    if not can_manage_sip(request.user):
        return HttpResponseForbidden('Tidak berwenang')
    obj.status = 'DIAJUKAN'
    obj.tanggal_pengajuan = timezone.now()
    obj.save(update_fields=['status', 'tanggal_pengajuan', 'updated_at'])
    messages.success(request, 'SIP Barang Lainnya berhasil diteruskan ke pejabat penandatangan.')
    return redirect(request.META.get('HTTP_REFERER', 'barang_lainnya:sip_list'))


@login_required
@require_POST
def sip_setujui(request, pk):
    obj = get_object_or_404(SIPBarangLainnya, pk=pk)
    if not can_approve_sip_kendaraan(request.user):
        return HttpResponseForbidden('Tidak berwenang')
    obj.status = 'TERBIT'
    obj.tanggal_persetujuan = timezone.now()
    obj.disetujui_oleh = request.user
    obj.catatan = request.POST.get('catatan') or ''
    obj.save()
    messages.success(request, 'SIP Barang Lainnya disetujui.')
    return redirect('barang_lainnya:sip_detail', pk=obj.pk)


@login_required
@require_POST
def sip_tolak(request, pk):
    obj = get_object_or_404(SIPBarangLainnya, pk=pk)
    if not can_approve_sip_kendaraan(request.user):
        return HttpResponseForbidden('Tidak berwenang')
    alasan = request.POST.get('catatan_penolakan', '').strip()
    if not alasan:
        messages.error(request, 'Alasan penolakan wajib diisi.')
        return redirect('barang_lainnya:sip_detail', pk=obj.pk)
    obj.status = 'DITOLAK'
    obj.catatan_penolakan = alasan
    obj.save(update_fields=['status', 'catatan_penolakan', 'updated_at'])
    messages.success(request, 'SIP Barang Lainnya ditolak.')
    return redirect('barang_lainnya:sip_detail', pk=obj.pk)


@login_required
def sip_persetujuan_list(request):
    qs = _base_queryset(request.user).filter(status='DIAJUKAN')
    return render(request, 'barang_lainnya/persetujuan_list.html', {'objects': qs, 'page_title': 'Persetujuan SIP Barang Lainnya'})


def _generate_pdf_bytes(obj):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    except Exception as exc:
        return None, str(exc)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=10)
    style_title = ParagraphStyle('title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=16, spaceAfter=4)
    style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=10, leading=13, alignment=TA_LEFT)
    story = []
    logo_path = Path(__file__).resolve().parents[1] / 'static' / 'img' / 'logo-kemensos.png'
    if logo_path.exists():
        logo = Image(str(logo_path), width=2.0*cm, height=2.6*cm)
        kop = Table([[logo, Paragraph('<b>KEMENTERIAN SOSIAL REPUBLIK INDONESIA</b><br/><b>%s</b><br/>Jl. Salemba Raya No. 28, Jakarta Pusat 10430<br/>www.kemensos.go.id' % (obj.pemegang_sip.unit_kerja.nama_unit.upper() if obj.pemegang_sip and obj.pemegang_sip.unit_kerja else 'SEKRETARIAT JENDERAL'), style_center)]], colWidths=[2.5*cm, 13.5*cm])
    else:
        kop = Table([[Paragraph('<b>KEMENTERIAN SOSIAL REPUBLIK INDONESIA</b><br/><b>%s</b>' % (obj.pemegang_sip.unit_kerja.nama_unit.upper() if obj.pemegang_sip and obj.pemegang_sip.unit_kerja else 'SEKRETARIAT JENDERAL'), style_center)]], colWidths=[16*cm])
    kop.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LINEBELOW', (0,0), (-1,-1), 1, colors.black)]))
    story += [kop, Spacer(1, 0.4*cm)]
    story += [Paragraph('SURAT IZIN PEMAKAIAN BARANG LAINNYA', style_title), Paragraph(f'Nomor: {obj.nomor_sip}', style_center), Spacer(1, 0.3*cm)]
    story += [Paragraph('Yang bertanda tangan di bawah ini, memberikan izin pemakaian Barang Lainnya milik Kementerian Sosial Republik Indonesia sebagaimana tercantum dalam daftar berikut kepada pemegang SIP untuk dipergunakan sesuai ketentuan yang berlaku.', style_normal), Spacer(1, 0.3*cm)]
    data = [['NO.', 'NAMA BARANG', 'SPESIFIKASI (MERK/TIPE)', 'JUMLAH', 'SATUAN', 'NUP', 'SERIAL NUMBER (OPSIONAL)', 'KETERANGAN']]
    for idx, item in enumerate(obj.items.all(), start=1):
        data.append([str(idx), item.nama_barang, item.spesifikasi or '-', str(item.jumlah), item.satuan or '-', item.nup or '-', item.serial_number or '-', item.keterangan or '-'])
    tbl = Table(data, colWidths=[0.8*cm, 2.5*cm, 3.0*cm, 1.2*cm, 1.4*cm, 2.2*cm, 2.8*cm, 2.6*cm])
    tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.HexColor('#efefef')), ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('ALIGN',(0,0),(-1,-1),'CENTER'), ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('GRID',(0,0),(-1,-1),0.6, colors.black), ('FONTSIZE',(0,0),(-1,-1),8), ('LEADING',(0,0),(-1,-1),10)]))
    story += [tbl, Spacer(1, 0.35*cm)]
    info = Table([
        ['Pemegang SIP', ''],
        ['Nama', obj.pemegang_sip.nama if obj.pemegang_sip else '-'],
        ['NIP', obj.pemegang_sip.nip if obj.pemegang_sip else '-'],
        ['Jabatan', obj.pemegang_sip.jabatan if obj.pemegang_sip else '-'],
        ['Unit Kerja', obj.pemegang_sip.unit_kerja.nama_unit if obj.pemegang_sip and obj.pemegang_sip.unit_kerja else '-'],
    ], colWidths=[3*cm, 12.5*cm])
    info.setStyle(TableStyle([('SPAN',(0,0),(1,0)), ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('VALIGN',(0,0),(-1,-1),'TOP')]))
    story += [info, Spacer(1, 0.3*cm)]
    story += [Paragraph('<b>Ketentuan</b><br/>1. Barang yang diizinkan dipakai hanya untuk keperluan sebagaimana tercantum pada tujuan penggunaan.<br/>2. Pemegang SIP bertanggung jawab penuh atas keamanan dan kondisi barang selama masa pemakaian.<br/>3. Dilarang memindahtangankan, meminjamkan, atau mengalihkan penggunaan barang kepada pihak lain tanpa izin tertulis dari pejabat yang berwenang.<br/>4. Apabila terjadi kerusakan atau kehilangan, pemegang SIP wajib segera melaporkan kepada atasan langsung dan/atau pejabat pengelola barang paling lambat 1 (satu) hari kerja sejak diketahui.<br/>5. Setelah berakhirnya periode pemakaian, barang wajib dikembalikan dalam kondisi baik dan lengkap kepada pengelola barang.', style_normal), Spacer(1, 0.4*cm)]
    ttd = Table([[Paragraph('<b>Pemegang SIP</b><br/>%s<br/><br/><br/><br/><u><b>%s</b></u><br/>NIP. %s' % (timezone.localdate().strftime('%d %B %Y'), obj.pemegang_sip.nama if obj.pemegang_sip else '-', obj.pemegang_sip.nip if obj.pemegang_sip else '-'), style_center), Paragraph('<b>Pejabat Penandatangan</b><br/>%s<br/>%s<br/><br/><br/><u><b>%s</b></u><br/>NIP. %s' % (timezone.localdate().strftime('%d %B %Y'), obj.jabatan_pejabat_penandatangan or '-', obj.nama_pejabat_penandatangan or '-', obj.nip_pejabat_penandatangan or '-'), style_center)]], colWidths=[8*cm, 8*cm])
    story += [ttd]
    doc.build(story)
    return buffer.getvalue(), None


@login_required
def sip_generate_konsep_pdf(request, pk):
    obj = get_object_or_404(SIPBarangLainnya, pk=pk)
    content, err = _generate_pdf_bytes(obj)
    if err:
        return HttpResponse(f'Gagal generate PDF: {err}', status=500, content_type='text/plain')
    filename = f'sip_barang_lainnya_{obj.pk}.pdf'
    obj.file_konsep_pdf.save(filename, ContentFile(content), save=True)
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@login_required
def sip_export(request, fmt):
    qs = _base_queryset(request.user).annotate(total_barang=Count('items'))
    if fmt == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sip_barang_lainnya.csv"'
        writer = csv.writer(response)
        writer.writerow(['No SIP', 'Tanggal', 'Pemegang SIP', 'Periode', 'Status', 'Total Barang'])
        for obj in qs:
            writer.writerow([obj.nomor_sip, obj.tanggal_sip, obj.pemegang_sip.nama if obj.pemegang_sip else '-', obj.masa_berlaku_display, obj.get_status_display(), obj.total_barang])
        return response
    if fmt == 'xlsx':
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = 'SIP Barang Lainnya'
        ws.append(['No SIP', 'Tanggal', 'Pemegang SIP', 'Periode', 'Status', 'Total Barang'])
        for obj in qs:
            ws.append([obj.nomor_sip, str(obj.tanggal_sip), obj.pemegang_sip.nama if obj.pemegang_sip else '-', obj.masa_berlaku_display, obj.get_status_display(), obj.total_barang])
        out = BytesIO()
        wb.save(out)
        response = HttpResponse(out.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="sip_barang_lainnya.xlsx"'
        return response
    # pdf summary
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors
    except Exception as exc:
        return HttpResponse(f'reportlab belum tersedia: {exc}', status=500, content_type='text/plain')
    out = BytesIO()
    doc = SimpleDocTemplate(out, pagesize=landscape(A4))
    data = [['No SIP','Tanggal','Pemegang SIP','Periode','Status','Total Barang']]
    for obj in qs:
        data.append([obj.nomor_sip, str(obj.tanggal_sip), obj.pemegang_sip.nama if obj.pemegang_sip else '-', obj.masa_berlaku_display, obj.get_status_display(), str(obj.total_barang)])
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.lightgrey), ('GRID',(0,0),(-1,-1),0.5, colors.black)]))
    doc.build([table])
    response = HttpResponse(out.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sip_barang_lainnya.pdf"'
    return response
