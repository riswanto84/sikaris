from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView

from core.access import UnitScopedQuerysetMixin, UnitScopedFormMixin
from core.detail import GenericDetailMixin
from core.listing import SearchListMixin
from core.pdf_sip import generate_sip_rumah_pdf
from core.roles import (
    BMNRequiredMixin,
    VehicleViewRequiredMixin,
    SIPEditRequiredMixin,
    SekjenRequiredMixin,
    can_manage_sip,
    is_admin_system,
    is_pengelola_bmn,
)

from .forms import SIPRumahDinasForm, SIPRumahCalonPenggunaTTEUploadForm, SIPRumahSekjenTTEUploadForm
from .models import SIPRumahDinas
from master.models import Pegawai


class SafeDeleteMixin:
    template_name = 'includes/confirm_delete.html'
    success_message = 'Data berhasil dihapus.'
    protected_message = 'Data tidak dapat dihapus karena masih digunakan oleh data lain.'

    def form_valid(self, form):
        try:
            messages.success(self.request, self.success_message)
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return redirect(self.get_success_url())


def _is_bmn_operator(user):
    return is_pengelola_bmn(user) and not is_admin_system(user)


def _user_can_manage_sip(user_or_request):
    user = getattr(user_or_request, 'user', user_or_request)
    return can_manage_sip(user)


def _user_can_approve_sip_rumah_as_sekjen(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name__in=['Admin System', 'Sekretaris Jenderal']).exists()
        )
    )


def _apply_search_filter(request, qs, search_fields):
    q = (request.GET.get('q') or '').strip()
    selected_field = (request.GET.get('search_field') or 'ALL').strip()
    if not q or not search_fields:
        return qs
    available_fields = [field for field, _label in search_fields]
    fields_to_search = available_fields
    if selected_field != 'ALL' and selected_field in available_fields:
        fields_to_search = [selected_field]
    query = Q()
    for field in fields_to_search:
        query |= Q(**{f'{field}__icontains': q})
    return qs.filter(query)


class SIPRumahDinasListView(BMNRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    template_name = 'rumah_dinas/sip_list.html'
    select_related = ['rumah_dinas', 'pegawai', 'pegawai__unit_kerja', 'penghuni', 'penghuni__unit_kerja']
    search_fields = [
        ('nomor_sip', 'Nomor SIP'),
        ('rumah_dinas__kode_rumah', 'Kode Rumah'),
        ('rumah_dinas__nama_rumah', 'Nama Rumah'),
        ('rumah_dinas__alamat', 'Alamat Rumah'),
        ('rumah_dinas__kondisi', 'Kondisi Rumah'),
        ('pegawai__nama', 'Nama Pemegang SIP'),
        ('penghuni__nama', 'Nama Penghuni Aktual'),
        ('pegawai__nip', 'NIP Pegawai'),
        ('pegawai__jabatan', 'Jabatan Pegawai'),
        ('pegawai__unit_kerja__nama_unit', 'Unit Kerja Pegawai'),
        ('pejabat_penandatangan', 'Pejabat Penandatangan'),
        ('status', 'Status SIP'),
        ('status_bayar_pnbp', 'Status Bayar PNBP'),
        ('tahun_pnbp', 'Tahun PNBP'),
        ('catatan', 'Catatan'),
    ]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['can_access_sip'] = can_manage_sip(self.request.user)
        ctx['can_submit_sip_rumah_from_list'] = can_manage_sip(self.request.user)
        ctx['submit_sip_rumah_button_label'] = 'Teruskan'
        return ctx


def _sip_rumah_form_context(obj=None):
    preview_docs = []
    if obj:
        def add_doc(label, f):
            if not f:
                return
            try:
                preview_docs.append({'label': label, 'url': f.url, 'is_pdf': str(f.name).lower().endswith('.pdf')})
            except Exception:
                pass
        add_doc('Preview Konsep PDF SIP Rumah Negara', getattr(obj, 'file_konsep_pdf', None))
        add_doc('Preview SIP Rumah Negara Final TTE Sekjen/BSrE', getattr(obj, 'file_signed_pdf', None) or getattr(obj, 'dokumen_sip', None))
    return {'sip_form_preview_docs': preview_docs}


def _pejabat_penandatangan_jabatan_map():
    return {
        str(p.id): (p.jabatan or '')
        for p in Pegawai.objects.only('id', 'jabatan').order_by('nama')
    }


class SIPRumahDinasCreateView(BMNRequiredMixin, UnitScopedFormMixin, CreateView):
    model = SIPRumahDinas
    form_class = SIPRumahDinasForm
    template_name = 'rumah_dinas/form.html'
    success_url = reverse_lazy('rumah_dinas:sip_list')

    def form_valid(self, form):
        form.instance.dibuat_oleh = self.request.user
        # Pengelola BMN mengisi data lalu sistem membuat konsep PDF.
        form.instance.status = 'DRAFT'
        response = super().form_valid(form)
        try:
            generate_sip_rumah_pdf(self.object, concept=True)
            messages.success(self.request, 'SIP Rumah Negara berhasil dibuat dan konsep PDF otomatis digenerate. Silakan cek preview PDF di bawah halaman detail, lalu ajukan ke Sekretaris Jenderal.')
        except Exception as exc:
            messages.warning(self.request, f'SIP Rumah Negara berhasil dibuat, tetapi konsep PDF belum berhasil digenerate: {exc}')
        return response

    def get_success_url(self):
        return reverse('rumah_dinas:sip_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_sip_rumah_form_context(self.object if hasattr(self, 'object') else None))
        ctx['pejabat_penandatangan_jabatan_map'] = _pejabat_penandatangan_jabatan_map()
        ctx['submit_label'] = 'Buat / Generate SIP Rumah Negara'
        return ctx


class SIPRumahDinasUpdateView(SIPEditRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    form_class = SIPRumahDinasForm
    template_name = 'rumah_dinas/form.html'
    success_url = reverse_lazy('rumah_dinas:sip_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status not in ['DRAFT', 'DITOLAK'] and not request.user.is_superuser:
            messages.error(request, 'SIP Rumah Negara hanya dapat diedit saat berstatus Draft/Konsep atau Ditolak.')
            return redirect('rumah_dinas:sip_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.instance.status == 'DITOLAK':
            form.instance.status = 'DRAFT'
        response = super().form_valid(form)
        try:
            generate_sip_rumah_pdf(self.object, concept=True)
            messages.success(self.request, 'Data SIP Rumah Negara berhasil diperbarui dan konsep PDF otomatis digenerate ulang.')
        except Exception as exc:
            messages.warning(self.request, f'Data berhasil diperbarui, tetapi konsep PDF belum berhasil digenerate ulang: {exc}')
        return response

    def get_success_url(self):
        return reverse('rumah_dinas:sip_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_sip_rumah_form_context(self.object))
        ctx['pejabat_penandatangan_jabatan_map'] = _pejabat_penandatangan_jabatan_map()
        ctx['submit_label'] = 'Simpan / Generate Ulang SIP Rumah Negara'
        return ctx


class SIPRumahDinasDetailView(VehicleViewRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    detail_title = 'Detail SIP Rumah Negara'
    back_url_name = 'rumah_dinas:sip_list'
    edit_url_name = 'rumah_dinas:sip_update'
    delete_url_name = 'rumah_dinas:sip_delete'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        user = self.request.user
        status = str(getattr(obj, 'status', '') or '').upper()
        status_tte = str(getattr(obj, 'status_tte', '') or '').upper()
        is_bmn_operator = _is_bmn_operator(user)
        can_edit_draft = status in ['DRAFT', 'DITOLAK']
        can_approve = _user_can_approve_sip_rumah_as_sekjen(user)

        approval_docs = []

        def add_approval_doc(label, f):
            if not f:
                return
            try:
                approval_docs.append({
                    'label': label,
                    'url': f.url,
                    'is_pdf': str(f.name).lower().endswith('.pdf'),
                })
            except Exception:
                pass

        # Samakan konsep preview dengan SIP Kendaraan:
        # final TTE Sekjen/BSrE -> TTE calon pengguna -> konsep PDF.
        final_pdf = getattr(obj, 'file_signed_pdf', None) or getattr(obj, 'dokumen_sip', None) or getattr(obj, 'file_final_pdf', None)
        calon_pengguna_pdf = getattr(obj, 'file_tte_calon_pengguna', None)
        konsep_pdf = getattr(obj, 'file_konsep_pdf', None)
        if final_pdf and (status in ['TERBIT', 'SELESAI', 'MENUNGGU_TTE', 'DISETUJUI'] or status_tte == 'SUDAH_TTE'):
            add_approval_doc('Preview SIP Rumah Negara Final TTE Sekjen/BSrE', final_pdf)
        elif calon_pengguna_pdf:
            add_approval_doc('Preview SIP Rumah Negara TTE Calon Pengguna Rumah', calon_pengguna_pdf)
        elif konsep_pdf:
            add_approval_doc('Preview Konsep PDF SIP Rumah Negara', konsep_pdf)

        ctx['dokumen_sip_url'] = None
        ctx['dokumen_sip_is_pdf'] = False
        ctx.update({
            'approval_docs': approval_docs,
            'can_generate_concept_pdf': is_bmn_operator and status in ['DRAFT', 'DITOLAK', 'DIAJUKAN', 'KONSEP'],
            'can_submit_to_sekjen': is_bmn_operator and can_edit_draft,
            'can_upload_tte_calon_pengguna_rumah': False,
            'has_konsep_pdf_rumah_for_tte': bool(getattr(obj, 'file_konsep_pdf', None) or getattr(obj, 'dokumen_sip', None)),
            'can_approve_as_sekjen': can_approve,
            'can_upload_tte_sekjen_rumah': can_approve and status == 'TERBIT' and status_tte != 'SUDAH_TTE',
            'approval_title': 'Persetujuan Pejabat Penandatangan - SIP Rumah Negara',
        })

        next_url = (self.request.GET.get('next') or '').strip()
        from_page = (self.request.GET.get('from') or '').strip().lower()
        referer = (self.request.META.get('HTTP_REFERER') or '').lower()

        # Perbaikan tombol Kembali untuk role Sekjen.
        # Detail SIP Rumah Negara dapat dibuka dari menu Persetujuan Sekjen,
        # notifikasi, atau setelah aksi Setujui/Tolak/Upload TTE. Pada kondisi
        # tersebut parameter from/next bisa hilang, sehingga fallback lama
        # mengarah ke daftar SIP umum Pengelola BMN. Untuk user Sekjen/Admin,
        # default Kembali harus selalu ke Persetujuan Sekjen - SIP Rumah Negara,
        # kecuali ada next URL yang aman.
        if next_url.startswith('/') and not next_url.startswith('//'):
            ctx['back_url'] = next_url
        elif (
            can_approve
            or from_page in ['approval', 'persetujuan', 'sekjen']
            or 'persetujuan-sekjen/sip-rumah' in referer
        ):
            ctx['back_url'] = reverse('rumah_dinas:sekjen_sip_rumah_list')

        if not can_edit_draft:
            ctx['edit_url'] = None
            ctx['delete_url'] = None
        return ctx


class SIPRumahDinasDeleteView(BMNRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'sip_rumah'
    model = SIPRumahDinas
    success_url = reverse_lazy('rumah_dinas:sip_list')
    success_message = 'SIP rumah negara berhasil dihapus.'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status not in ['DRAFT', 'DITOLAK'] and not request.user.is_superuser:
            messages.error(request, 'SIP Rumah Negara hanya dapat dihapus saat berstatus Draft/Konsep atau Ditolak.')
            return redirect('rumah_dinas:sip_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)


@login_required
@require_POST
def sip_generate_konsep_pdf(request, pk):
    sip = get_object_or_404(SIPRumahDinas, pk=pk)
    is_bmn_operator = _is_bmn_operator(request.user)
    if not (is_bmn_operator and sip.status in ['DRAFT', 'DITOLAK', 'DIAJUKAN']):
        messages.error(request, 'Generate Konsep PDF SIP Rumah Negara hanya dapat dilakukan oleh Pengelola BMN pada data yang belum final.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    generate_sip_rumah_pdf(sip, concept=True)
    messages.success(request, 'Konsep/Draft PDF SIP Rumah Negara berhasil dibuat. Preview PDF tampil di bawah halaman detail. Selanjutnya ajukan ke Sekretaris Jenderal untuk persetujuan.')
    return redirect('rumah_dinas:sip_detail', pk=pk)


@login_required
@require_POST
def sip_upload_tte_calon_pengguna_pdf(request, pk):
    if not (_is_bmn_operator(request.user) or is_admin_system(request.user)):
        messages.error(request, 'Upload TTE calon pengguna rumah hanya dapat dilakukan oleh Pengelola BMN/pengusul.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    sip = get_object_or_404(SIPRumahDinas, pk=pk)
    if str(getattr(sip, 'status', '') or '').upper() not in ['DRAFT', 'DITOLAK', 'DIAJUKAN', 'KONSEP']:
        messages.error(request, 'Upload TTE calon pengguna rumah hanya dapat dilakukan sebelum SIP Rumah Negara disetujui/terbit.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    form = SIPRumahCalonPenggunaTTEUploadForm(request.POST, request.FILES, instance=sip)
    if not form.is_valid():
        for field_errors in form.errors.values():
            for err in field_errors:
                messages.error(request, err)
        return redirect('rumah_dinas:sip_detail', pk=pk)
    sip = form.save(commit=False)
    sip.status_tte_calon_pengguna = 'SUDAH_TTE'
    sip.tanggal_tte_calon_pengguna = timezone.now()
    sip.catatan_tte_calon_pengguna = 'File konsep SIP Rumah Negara yang sudah TTE oleh calon pengguna rumah diupload oleh Pengelola BMN.'
    sip.save(update_fields=['file_tte_calon_pengguna', 'status_tte_calon_pengguna', 'tanggal_tte_calon_pengguna', 'catatan_tte_calon_pengguna', 'updated_at'])
    messages.success(request, 'File SIP Rumah Negara yang sudah TTE oleh calon pengguna rumah berhasil diupload. SIP sudah dapat diajukan ke Sekjen.')
    return redirect('rumah_dinas:sip_detail', pk=pk)


@login_required
@require_POST
def sip_ajukan_sekjen(request, pk):
    if not _user_can_manage_sip(request):
        messages.error(request, 'Anda tidak memiliki akses untuk meneruskan SIP ke Pejabat Penandatangan.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    sip = get_object_or_404(SIPRumahDinas, pk=pk)
    if sip.status not in ['DRAFT', 'DITOLAK']:
        messages.error(request, 'Hanya SIP berstatus Draft/Konsep atau Ditolak yang dapat diteruskan.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    if not sip.file_konsep_pdf:
        messages.error(request, 'Generate Konsep PDF terlebih dahulu sebelum SIP Rumah Negara diteruskan.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    sip.status = 'DIAJUKAN'
    sip.tanggal_pengajuan = timezone.now()
    sip.catatan_penolakan = ''
    sip.save(update_fields=['status', 'tanggal_pengajuan', 'catatan_penolakan', 'updated_at'])
    messages.success(request, 'SIP Rumah Negara berhasil diteruskan ke Pejabat Penandatangan untuk persetujuan.')
    return redirect('rumah_dinas:sip_detail', pk=pk)


@login_required
@require_POST
def sip_setujui_sekjen(request, pk):
    if not _user_can_approve_sip_rumah_as_sekjen(request.user):
        messages.error(request, 'Hanya Sekretaris Jenderal/Admin System yang dapat menyetujui SIP Rumah Negara.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    sip = get_object_or_404(SIPRumahDinas, pk=pk)
    if sip.status != 'DIAJUKAN':
        messages.error(request, 'Hanya SIP Rumah Negara berstatus Diajukan yang dapat disetujui.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    keterangan_persetujuan = (request.POST.get('keterangan_persetujuan') or '').strip()
    sip.status = 'TERBIT'
    sip.status_tte = 'SIAP_TTE'
    sip.tanggal_persetujuan = timezone.now()
    sip.disetujui_oleh = request.user
    sip.catatan_penolakan = ''
    if keterangan_persetujuan:
        sip.catatan = keterangan_persetujuan
    sip.catatan_tte = 'SIP Rumah Negara sudah disetujui dan berstatus Terbit. Menunggu upload SIP final yang sudah TTE Sekjen/BSrE.'
    sip.save(update_fields=['status', 'status_tte', 'tanggal_persetujuan', 'disetujui_oleh', 'catatan_penolakan', 'catatan', 'catatan_tte', 'updated_at'])
    messages.success(request, 'SIP Rumah Negara disetujui dan status langsung menjadi Terbit. Silakan upload file SIP final yang sudah TTE Sekjen/BSrE.')
    return redirect('rumah_dinas:sip_detail', pk=pk)


@login_required
@require_POST
def sip_upload_tte_sekjen_pdf(request, pk):
    if not _user_can_approve_sip_rumah_as_sekjen(request.user):
        messages.error(request, 'Hanya Sekretaris Jenderal/Admin System yang dapat mengupload SIP TTE Sekjen/BSrE.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    sip = get_object_or_404(SIPRumahDinas, pk=pk)
    if str(getattr(sip, 'status', '') or '').upper() != 'TERBIT':
        messages.error(request, 'Upload SIP TTE Sekjen/BSrE hanya dapat dilakukan setelah SIP Rumah Negara disetujui dan status menjadi Terbit.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    form = SIPRumahSekjenTTEUploadForm(request.POST, request.FILES, instance=sip)
    if not form.is_valid():
        for field_errors in form.errors.values():
            for err in field_errors:
                messages.error(request, err)
        return redirect('rumah_dinas:sip_detail', pk=pk)
    sip = form.save(commit=False)
    sip.status = 'TERBIT'
    sip.status_tte = 'SUDAH_TTE'
    sip.tanggal_tte = timezone.now()
    sip.catatan_tte = 'File SIP Rumah Negara final yang sudah TTE Sekjen/BSrE diupload oleh Sekretaris Jenderal/Admin System.'
    if sip.file_signed_pdf:
        sip.dokumen_sip = sip.file_signed_pdf
    sip.save(update_fields=['file_signed_pdf', 'dokumen_sip', 'status', 'status_tte', 'tanggal_tte', 'catatan_tte', 'updated_at'])
    messages.success(request, 'File SIP Rumah Negara yang sudah TTE Sekjen/BSrE berhasil diupload.')
    return redirect('rumah_dinas:sip_detail', pk=pk)


@login_required
@require_POST
def sip_tolak_sekjen(request, pk):
    if not _user_can_approve_sip_rumah_as_sekjen(request.user):
        messages.error(request, 'Hanya Sekretaris Jenderal/Admin System yang dapat menolak SIP Rumah Negara.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    sip = get_object_or_404(SIPRumahDinas, pk=pk)
    if sip.status != 'DIAJUKAN':
        messages.error(request, 'Hanya SIP Rumah Negara berstatus Diajukan yang dapat ditolak.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    alasan = (request.POST.get('alasan_penolakan') or request.POST.get('catatan_penolakan') or '').strip()
    keterangan = (request.POST.get('keterangan_penolakan') or '').strip()
    if not alasan:
        messages.error(request, 'Alasan penolakan wajib diisi.')
        return redirect('rumah_dinas:sip_detail', pk=pk)
    catatan = alasan if not keterangan else f'Alasan: {alasan}\nKeterangan: {keterangan}'
    sip.status = 'DITOLAK'
    sip.catatan_penolakan = catatan
    sip.tanggal_persetujuan = timezone.now()
    sip.disetujui_oleh = request.user
    sip.save(update_fields=['status', 'catatan_penolakan', 'tanggal_persetujuan', 'disetujui_oleh', 'updated_at'])
    messages.warning(request, 'SIP Rumah Negara ditolak dan dikembalikan untuk perbaikan.')
    return redirect('rumah_dinas:sip_detail', pk=pk)


def _stringify(value):
    if value is None:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime('%d/%m/%Y')
    return str(value)


def _sip_rumah_export_rows(qs):
    rows = []
    for o in qs.select_related('rumah_dinas', 'pegawai', 'penghuni', 'rumah_dinas__unit_kerja'):
        rows.append([
            o.nomor_sip,
            o.tanggal_sip,
            getattr(o.rumah_dinas, 'kode_rumah', '') if o.rumah_dinas_id else '',
            getattr(o.rumah_dinas, 'nama_rumah', '') if o.rumah_dinas_id else '',
            getattr(o.rumah_dinas.unit_kerja, 'nama_unit', '') if o.rumah_dinas_id and o.rumah_dinas.unit_kerja_id else '',
            getattr(o.pegawai, 'nama', '') if o.pegawai_id else '',
            getattr(o.pegawai, 'nip', '') if o.pegawai_id else '',
            getattr(o.penghuni, 'nama', '') if o.penghuni_id else '',
            o.tanggal_mulai,
            o.tanggal_akhir,
            o.get_status_display(),
            o.status_aktif_display,
            o.pejabat_penandatangan or '',
        ])
    return rows


def _export_rows_response(fmt, filename_base, title, headers, rows):
    fmt = (fmt or 'xlsx').lower()
    if fmt == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename_base}.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([_stringify(v) for v in row])
        return response
    if fmt == 'pdf':
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename_base}.pdf"'
        doc = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=0.8*cm, rightMargin=0.8*cm, topMargin=0.8*cm, bottomMargin=0.8*cm)
        styles = getSampleStyleSheet()
        data = [headers] + [[Paragraph(_stringify(v), styles['BodyText']) for v in row] for row in rows[:500]]
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1D4ED8')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#CBD5E1')),('FONTSIZE',(0,0),(-1,-1),7),('VALIGN',(0,0),(-1,-1),'TOP')]))
        doc.build([Paragraph(f'<b>{title}</b>', styles['Title']), Spacer(1,0.2*cm), table])
        return response
    from openpyxl import Workbook
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
    wb = Workbook()
    ws = wb.active
    ws.title = 'Export SIP'
    ws.append(headers)
    for row in rows:
        ws.append([_stringify(v) for v in row])
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = 'A2'
    wb.save(response)
    return response


@login_required
def sip_export(request, fmt):
    from core.access import scope_queryset_by_user
    qs = scope_queryset_by_user(SIPRumahDinas.objects.all(), request.user, 'sip_rumah')
    qs = _apply_search_filter(request, qs, SIPRumahDinasListView.search_fields).order_by('-tanggal_sip')
    headers = ['Nomor SIP', 'Tanggal SIP', 'Kode Register', 'Rumah Negara', 'Unit Kerja', 'Pemegang SIP', 'NIP', 'Penghuni Aktual', 'Tanggal Mulai', 'Tanggal Akhir', 'Status Proses', 'Status Aktif/Non Aktif', 'Pejabat Penandatangan']
    return _export_rows_response(fmt, 'export_sip_rumah_negara', 'Export SIP Rumah Negara', headers, _sip_rumah_export_rows(qs))


class SekjenSIPRumahListView(SekjenRequiredMixin, SearchListMixin, ListView):
    model = SIPRumahDinas
    template_name = 'rumah_dinas/sekjen_sip_list.html'
    paginate_by = 15
    select_related = ['rumah_dinas', 'pegawai', 'pegawai__unit_kerja']
    search_fields = [
        ('nomor_sip', 'Nomor SIP'),
        ('rumah_dinas__kode_rumah', 'Kode Rumah'),
        ('rumah_dinas__alamat', 'Alamat Rumah'),
        ('rumah_dinas__nama_rumah', 'Nama Rumah'),
        ('pegawai__nama', 'Nama Pegawai'),
        ('pegawai__nip', 'NIP Pegawai'),
        ('status', 'Status SIP'),
    ]

    def get_queryset(self):
        # Pejabat penandatangan/Sekjen melihat data SIP Rumah Negara yang sudah diteruskan.
        # Admin System tetap dapat melihat seluruh data untuk pengawasan.
        qs = SIPRumahDinas.objects.select_related(*self.select_related).all()
        qs = _apply_search_filter(self.request, qs, self.search_fields)
        return qs.order_by('-tanggal_pengajuan', '-tanggal_sip', '-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['approval_title'] = 'Persetujuan Pejabat Penandatangan - SIP Rumah Negara'
        return ctx
