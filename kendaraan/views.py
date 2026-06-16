from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from core.roles import BMNRequiredMixin, MaintenanceRequiredMixin, VehicleViewRequiredMixin, SIPEditRequiredMixin
from core.listing import SearchListMixin
from core.detail import GenericDetailMixin
from core.export_utils import apply_search_filter, export_queryset
from core.access import UnitScopedQuerysetMixin, UnitScopedFormMixin, scope_queryset_by_user
from master.models import Kendaraan

from .models import (
    SIPKendaraan,
    ServiceKendaraan,
    RiwayatKondisiKendaraan,
    BuktiKuitansiServiceKendaraan,
)

from .forms import (
    SIPKendaraanForm,
    SIPKendaraanPengusulTTEUploadForm,
    SIPKendaraanBSREUploadForm,
    ServiceKendaraanForm,
    RiwayatKondisiKendaraanForm,
)


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


def get_kendaraan_foto_map(user=None):
    """
    Membuat mapping:
    {
        "1": "/media/kendaraan/galeri/foto1.jpg",
        "2": "/media/kendaraan/galeri/foto2.jpg",
    }

    Digunakan oleh JavaScript di service_form.html
    untuk menampilkan foto kendaraan berdasarkan pilihan dropdown.
    """
    kendaraan_foto_map = {}

    kendaraan_qs = Kendaraan.objects.prefetch_related('galeri_foto').all()
    if user is not None:
        kendaraan_qs = scope_queryset_by_user(kendaraan_qs, user, 'kendaraan')
    kendaraan_list = kendaraan_qs

    for kendaraan in kendaraan_list:
        foto_pertama = kendaraan.galeri_foto.first()

        if foto_pertama:
            kendaraan_foto_map[str(kendaraan.id)] = foto_pertama.foto.url

    return kendaraan_foto_map


class SIPKendaraanListView(VehicleViewRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    template_name = 'kendaraan/sip_list.html'
    select_related = ['kendaraan', 'pegawai', 'kendaraan__unit_kerja', 'pegawai__unit_kerja']
    search_fields = [
        ('nomor_sip', 'Nomor SIP'),
        ('kendaraan__kode_kendaraan', 'Kode Kendaraan'),
        ('kendaraan__nomor_polisi', 'Nomor Polisi'),
        ('kendaraan__merek', 'Merek Kendaraan'),
        ('kendaraan__tipe', 'Tipe Kendaraan'),
        ('pegawai__nama', 'Nama Pegawai'),
        ('pegawai__nip', 'NIP Pegawai'),
        ('pegawai__jabatan', 'Jabatan Pegawai'),
        ('pegawai__unit_kerja__nama_unit', 'Unit Kerja Pegawai'),
        ('jenis_pemakaian', 'Jenis Pemakaian'),
        ('tujuan_pemakaian', 'Tujuan Pemakaian'),
        ('lokasi_penggunaan', 'Lokasi Penggunaan'),
        ('pejabat_penandatangan', 'Pejabat Penandatangan'),
        ('status', 'Status SIP'),
        ('catatan', 'Catatan'),
    ]


class SIPKendaraanCreateView(BMNRequiredMixin, UnitScopedFormMixin, CreateView):
    model = SIPKendaraan
    form_class = SIPKendaraanForm
    template_name = 'kendaraan/sip_form.html'
    success_url = reverse_lazy('kendaraan:sip_list')

    def form_valid(self, form):
        # Pengelola BMN hanya membuat Draft/Konsep.
        # Pengajuan dilakukan lewat tombol Ajukan pada halaman detail.
        form.instance.dibuat_oleh = self.request.user
        form.instance.status = 'DRAFT'
        return super().form_valid(form)


class SIPKendaraanUpdateView(SIPEditRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    form_class = SIPKendaraanForm
    template_name = 'kendaraan/sip_form.html'
    success_url = reverse_lazy('kendaraan:sip_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status not in ['DRAFT', 'DITOLAK'] and not request.user.is_superuser:
            messages.error(request, 'SIP Kendaraan hanya dapat diedit saat berstatus Draft/Konsep atau Ditolak.')
            return redirect('kendaraan:sip_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Jika revisi dari status Ditolak, kembalikan menjadi Draft/Konsep.
        if form.instance.status == 'DITOLAK':
            form.instance.status = 'DRAFT'
        return super().form_valid(form)


class SIPKendaraanDetailView(VehicleViewRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    detail_title = 'Detail SIP Kendaraan'
    back_url_name = 'kendaraan:sip_list'
    edit_url_name = 'kendaraan:sip_update'
    delete_url_name = 'kendaraan:sip_delete'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        # Sinkronkan snapshot pejabat penerbit ketika konfigurasi Master Unit Kerja
        # baru diisi setelah SIP dibuat. Ini mencegah detail/ajukan tetap kosong
        # padahal pejabat pada Master Unit Kerja sudah dikonfigurasi.
        if not obj.pejabat_penerbit_sip_kendaraan_id or not obj.nama_pejabat_penerbit_sip_kendaraan:
            try:
                from .sip_penerbit import apply_snapshot_penerbit_sip_kendaraan
                apply_snapshot_penerbit_sip_kendaraan(obj, force=True)
                obj.save(update_fields=[
                    'pejabat_penerbit_sip_kendaraan',
                    'nama_pejabat_penerbit_sip_kendaraan',
                    'nip_pejabat_penerbit_sip_kendaraan',
                    'jabatan_pejabat_penerbit_sip_kendaraan',
                    'pejabat_penandatangan',
                    'updated_at',
                ])
            except Exception:
                pass
        approval_docs = []

        def add_approval_doc(label, f):
            if not f:
                return
            try:
                approval_docs.append({
                    'label': label,
                    'url': f.url,
                    'is_pdf': str(f.name).lower().endswith('.pdf')
                })
            except Exception:
                pass

        # Aturan preview dokumen SIP Kendaraan:
        # - Jika SIP sudah sampai tahap final/TTE pejabat penerbit, tampilkan hanya file final terakhir.
        # - Jika belum final tetapi sudah ada TTE pengusul, tampilkan file TTE pengusul.
        # - Jika belum ada TTE pengusul, tampilkan konsep PDF untuk proses awal.
        # Dengan aturan ini detail tidak lagi menampilkan banyak versi PDF yang membingungkan.
        final_pdf = getattr(obj, 'file_signed_pdf', None) or getattr(obj, 'dokumen_sip', None) or getattr(obj, 'file_final_pdf', None)
        pengusul_pdf = getattr(obj, 'file_tte_pengusul', None)
        konsep_pdf = getattr(obj, 'file_konsep_pdf', None)
        status = str(getattr(obj, 'status', '') or '').upper()
        status_tte = str(getattr(obj, 'status_tte', '') or '').upper()

        if final_pdf and (status in ['TERBIT', 'SELESAI', 'MENUNGGU_TTE', 'DISETUJUI'] or status_tte == 'SUDAH_TTE'):
            add_approval_doc('Preview SIP Kendaraan Final TTE BSrE', final_pdf)
        elif pengusul_pdf:
            add_approval_doc('Preview SIP Kendaraan TTE Pegawai Pengusul', pengusul_pdf)
        elif konsep_pdf:
            add_approval_doc('Preview Konsep PDF SIP Kendaraan', konsep_pdf)
        user = self.request.user
        from .sip_penerbit import get_label_tujuan_pengajuan_sip_kendaraan
        can_edit_draft = obj.status in ['DRAFT', 'DITOLAK']
        is_bmn_operator = is_pengelola_bmn(user) and not is_admin_system(user)

        # Pengelola BMN tetap sebagai pengusul, tetapi sesuai aturan koreksi terakhir
        # pada detail SIP Kendaraan tombol Edit, Hapus, dan Generate Konsep PDF tetap tersedia
        # selama status masih belum final/dapat direvisi. Upload PDF TTE BSrE tetap hanya untuk pejabat penerbit.
        can_approve_obj = False if is_bmn_operator else can_approve_sip_kendaraan_object(user, obj)
        can_generate_concept_as_bmn = is_bmn_operator and obj.status in ['DRAFT', 'DITOLAK', 'DIAJUKAN']

        # Preview SIP Kendaraan dikelola melalui approval_docs agar hanya satu versi dokumen
        # yang muncul sesuai tahap proses. Hindari duplikasi dari preview dokumen_sip generic.
        ctx['dokumen_sip_url'] = None
        ctx['dokumen_sip_is_pdf'] = False

        ctx.update({
            'approval_docs': approval_docs,
            # Generate konsep PDF hanya untuk Pengelola BMN sebagai pengusul.
            # Pejabat penerbit cukup melakukan Setujui/Tolak dan tidak generate ulang PDF.
            'can_generate_concept_pdf': can_generate_concept_as_bmn,
            # Tampilkan form upload TTE calon pemegang untuk Pengelola BMN selama status belum final.
            # Gunakan status_upper agar data lama dengan status 'Draft', 'draft', atau variasi label lain tetap terbaca.
            'can_upload_tte_pengusul': is_bmn_operator and status in ['DRAFT', 'DITOLAK', 'DIAJUKAN', 'KONSEP'] and str(getattr(obj, 'status_tte_pengusul', 'BELUM') or '').upper() != 'SUDAH_TTE',
            'has_konsep_pdf_for_tte_pengusul': bool(getattr(obj, 'file_konsep_pdf', None) or getattr(obj, 'dokumen_sip', None)),
            'can_submit_to_kabiro': is_bmn_operator and can_edit_draft,
            'can_submit_to_sekjen': False,
            'can_approve_as_kabiro': can_approve_obj,
            'can_approve_as_sekjen': False,
            # Setelah pejabat penerbit menyetujui, status SIP langsung TERBIT.
            # Pejabat penerbit kemudian dapat mengupload file SIP final yang sudah TTE
            # oleh Kepala Biro/Sekretaris/Kepala Sentra/Kepala Balai.
            'can_upload_sip_kendaraan_bsre': (not is_bmn_operator) and can_approve_sip_kendaraan_object(user, obj) and obj.status == 'TERBIT',
            'approval_title': 'Persetujuan Pejabat Penerbit SIP Kendaraan',
            'tujuan_pengajuan_sip_kendaraan': get_label_tujuan_pengajuan_sip_kendaraan(obj),
        })

        # Jika halaman detail dibuka dari menu Persetujuan Pejabat Penerbit,
        # tombol Kembali harus kembali ke daftar persetujuan, bukan ke Daftar SIP umum.
        next_url = (self.request.GET.get('next') or '').strip()
        from_page = (self.request.GET.get('from') or '').strip().lower()
        referer = (self.request.META.get('HTTP_REFERER') or '').lower()
        if next_url.startswith('/') and not next_url.startswith('//'):
            ctx['back_url'] = next_url
        elif from_page in ['approval', 'persetujuan'] or 'persetujuan-kabiro/sip-kendaraan' in referer or 'persetujuan-sekjen/sip-kendaraan' in referer:
            ctx['back_url'] = reverse('kendaraan:kabiro_sip_kendaraan_list')

        # Tombol Edit/Hapus tetap ada untuk Pengelola BMN selama status DRAFT/DITOLAK.
        # Untuk status yang sudah masuk proses/final, tombol edit/hapus disembunyikan.
        if not can_edit_draft:
            ctx['edit_url'] = None
            ctx['delete_url'] = None
        return ctx


class SIPKendaraanDeleteView(BMNRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    success_url = reverse_lazy('kendaraan:sip_list')
    success_message = 'SIP kendaraan berhasil dihapus.'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status not in ['DRAFT', 'DITOLAK'] and not request.user.is_superuser:
            messages.error(request, 'SIP Kendaraan hanya dapat dihapus saat berstatus Draft/Konsep atau Ditolak.')
            return redirect('kendaraan:sip_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)


class ServiceKendaraanListView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'service_kendaraan'
    model = ServiceKendaraan
    template_name = 'kendaraan/service_list.html'
    select_related = ['kendaraan', 'kendaraan__unit_kerja', 'dicatat_oleh']
    search_fields = [
        ('kendaraan__kode_kendaraan', 'Kode Kendaraan'),
        ('kendaraan__nomor_polisi', 'Nomor Polisi'),
        ('kendaraan__merek', 'Merek Kendaraan'),
        ('kendaraan__tipe', 'Tipe Kendaraan'),
        ('kendaraan__unit_kerja__nama_unit', 'Unit Kerja'),
        ('jenis_service', 'Jenis Service'),
        ('bengkel', 'Bengkel'),
        ('uraian_pekerjaan', 'Uraian Pekerjaan'),
        ('sparepart_diganti', 'Sparepart Diganti'),
        ('kondisi_sebelum', 'Kondisi Sebelum'),
        ('kondisi_sesudah', 'Kondisi Sesudah'),
        ('dicatat_oleh__username', 'Petugas Pencatat'),
    ]


class ServiceKendaraanCreateView(MaintenanceRequiredMixin, UnitScopedFormMixin, CreateView):
    model = ServiceKendaraan
    form_class = ServiceKendaraanForm
    template_name = 'kendaraan/service_form.html'
    success_url = reverse_lazy('kendaraan:service_list')

    def form_valid(self, form):
        form.instance.dicatat_oleh = self.request.user

        response = super().form_valid(form)

        for file in self.request.FILES.getlist('kuitansi_files'):
            BuktiKuitansiServiceKendaraan.objects.create(
                service=self.object,
                file=file,
                diupload_oleh=self.request.user
            )

        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['kendaraan_foto_map'] = get_kendaraan_foto_map(self.request.user)
        ctx['foto_kendaraan_aktif'] = None
        ctx['kuitansi_list'] = []

        return ctx


class ServiceKendaraanDetailView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'service_kendaraan'
    model = ServiceKendaraan
    detail_title = 'Detail Service Kendaraan'
    back_url_name = 'kendaraan:service_list'
    edit_url_name = 'kendaraan:service_update'
    delete_url_name = 'kendaraan:service_delete'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['service_kuitansi_list'] = self.object.bukti_kuitansi.all()
        return ctx


class ServiceKendaraanUpdateView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'service_kendaraan'
    model = ServiceKendaraan
    form_class = ServiceKendaraanForm
    template_name = 'kendaraan/service_form.html'
    success_url = reverse_lazy('kendaraan:service_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        for file in self.request.FILES.getlist('kuitansi_files'):
            BuktiKuitansiServiceKendaraan.objects.create(
                service=self.object,
                file=file,
                diupload_oleh=self.request.user
            )

        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['kendaraan_foto_map'] = get_kendaraan_foto_map(self.request.user)

        if self.object and self.object.kendaraan:
            foto_pertama = self.object.kendaraan.galeri_foto.first()
            ctx['foto_kendaraan_aktif'] = foto_pertama.foto.url if foto_pertama else None
        else:
            ctx['foto_kendaraan_aktif'] = None

        ctx['kuitansi_list'] = self.object.bukti_kuitansi.all()

        return ctx


class ServiceKendaraanDeleteView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'service_kendaraan'
    model = ServiceKendaraan
    success_url = reverse_lazy('kendaraan:service_list')
    success_message = 'Service kendaraan berhasil dihapus.'


@login_required
@require_POST
def kuitansi_service_delete(request, pk):
    kuitansi = get_object_or_404(BuktiKuitansiServiceKendaraan.objects.filter(service__in=scope_queryset_by_user(ServiceKendaraan.objects.all(), request.user, 'service_kendaraan')), pk=pk)
    service_id = kuitansi.service_id

    kuitansi.file.delete(save=False)
    kuitansi.delete()

    return redirect('kendaraan:service_update', pk=service_id)


class RiwayatKondisiListView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'kondisi_kendaraan'
    model = RiwayatKondisiKendaraan
    template_name = 'kendaraan/kondisi_list.html'
    select_related = ['kendaraan', 'kendaraan__unit_kerja', 'dicatat_oleh']
    search_fields = [
        ('kendaraan__kode_kendaraan', 'Kode Kendaraan'),
        ('kendaraan__nomor_polisi', 'Nomor Polisi'),
        ('kendaraan__merek', 'Merek Kendaraan'),
        ('kendaraan__tipe', 'Tipe Kendaraan'),
        ('kendaraan__unit_kerja__nama_unit', 'Unit Kerja'),
        ('kondisi', 'Kondisi'),
        ('uraian_kondisi', 'Uraian Kondisi'),
        ('dicatat_oleh__username', 'Petugas Pencatat'),
    ]


class RiwayatKondisiCreateView(MaintenanceRequiredMixin, UnitScopedFormMixin, CreateView):
    model = RiwayatKondisiKendaraan
    form_class = RiwayatKondisiKendaraanForm
    template_name = 'kendaraan/form.html'
    success_url = reverse_lazy('kendaraan:kondisi_list')

    def form_valid(self, form):
        form.instance.dicatat_oleh = self.request.user
        return super().form_valid(form)

class RiwayatKondisiDetailView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'kondisi_kendaraan'
    model = RiwayatKondisiKendaraan
    detail_title = 'Detail Riwayat Kondisi Kendaraan'
    back_url_name = 'kendaraan:kondisi_list'
    delete_url_name = 'kendaraan:kondisi_delete'


class RiwayatKondisiDeleteView(MaintenanceRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'kondisi_kendaraan'
    model = RiwayatKondisiKendaraan
    success_url = reverse_lazy('kendaraan:kondisi_list')
    success_message = 'Riwayat kondisi kendaraan berhasil dihapus.'

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView
from django.views.decorators.http import require_http_methods
from core.roles import KepalaBiroUmumRequiredMixin, can_manage_sip, can_approve_sip_kendaraan, can_approve_sip_kendaraan_object, is_pengelola_bmn, is_admin_system
from core.pdf_sip import generate_sip_kendaraan_pdf


def _user_can_manage_sip(request):
    return can_manage_sip(request.user)


def _apply_search_filter(request, qs, search_fields):
    """Apply server-side search for custom ListView get_queryset overrides.

    SearchListMixin cannot run automatically when a view overrides get_queryset.
    This helper keeps the behavior of the common search form on approval pages.
    """
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


@login_required
@require_POST
def sip_generate_konsep_pdf(request, pk):
    sip = get_object_or_404(SIPKendaraan, pk=pk)
    is_bmn_operator = is_pengelola_bmn(request.user) and not is_admin_system(request.user)

    # Pengelola BMN boleh generate konsep PDF untuk draft/revisi/pengajuan yang belum final.
    allowed_bmn = is_bmn_operator and sip.status in ['DRAFT', 'DITOLAK', 'DIAJUKAN']

    # Pejabat penerbit tidak perlu generate ulang PDF.
    # Generate konsep PDF hanya dilakukan Pengelola BMN sebelum TTE pegawai pengusul.
    if not allowed_bmn:
        messages.error(request, 'Generate Konsep PDF SIP Kendaraan hanya dapat dilakukan oleh Pengelola BMN pada data yang belum final.')
        return redirect('kendaraan:sip_detail', pk=pk)

    generate_sip_kendaraan_pdf(sip, concept=True)
    messages.success(request, 'Konsep/Draft PDF SIP Kendaraan berhasil dibuat. Selanjutnya lakukan TTE oleh pegawai pengusul, lalu upload file PDF yang sudah TTE pengusul sebelum diajukan ke pejabat penerbit.')
    return redirect('kendaraan:sip_detail', pk=pk)


@login_required
@require_POST
def sip_upload_tte_pengusul_pdf(request, pk):
    sip = get_object_or_404(SIPKendaraan, pk=pk)
    is_bmn_operator = is_pengelola_bmn(request.user) and not is_admin_system(request.user)
    if not (is_bmn_operator or is_admin_system(request.user)):
        messages.error(request, 'Upload TTE pegawai pengusul hanya dapat dilakukan oleh Pengelola BMN/pengusul.')
        return redirect('kendaraan:sip_detail', pk=pk)
    if str(getattr(sip, 'status', '') or '').upper() not in ['DRAFT', 'DITOLAK', 'DIAJUKAN', 'KONSEP']:
        messages.error(request, 'Upload TTE pegawai pengusul hanya dapat dilakukan saat SIP belum disetujui oleh pejabat penerbit.')
        return redirect('kendaraan:sip_detail', pk=pk)
    # Untuk menghindari kasus form upload tidak dapat digunakan pada data lama,
    # upload tetap diterima walaupun file_konsep_pdf belum tersimpan. Pengelola BMN
    # tetap diarahkan melalui pesan UI untuk generate konsep terlebih dahulu.

    form = SIPKendaraanPengusulTTEUploadForm(request.POST, request.FILES, instance=sip)
    if not form.is_valid():
        for field_errors in form.errors.values():
            for err in field_errors:
                messages.error(request, err)
        return redirect('kendaraan:sip_detail', pk=pk)

    sip = form.save(commit=False)
    sip.status_tte_pengusul = 'SUDAH_TTE'
    sip.tanggal_tte_pengusul = timezone.now()
    sip.catatan_tte_pengusul = 'File konsep SIP yang sudah TTE oleh pegawai pengusul diupload oleh Pengelola BMN.'
    sip.save(update_fields=['file_tte_pengusul', 'status_tte_pengusul', 'tanggal_tte_pengusul', 'catatan_tte_pengusul', 'updated_at'])
    messages.success(request, 'File SIP Kendaraan yang sudah TTE oleh pegawai pengusul berhasil diupload. SIP sudah dapat diajukan ke pejabat penerbit.')
    return redirect('kendaraan:sip_detail', pk=pk)


@login_required
@require_POST
def sip_ajukan_kabiro(request, pk):
    if not _user_can_manage_sip(request):
        messages.error(request, 'Anda tidak memiliki akses untuk mengajukan SIP ke pejabat penerbit.')
        return redirect('kendaraan:sip_detail', pk=pk)
    sip = get_object_or_404(SIPKendaraan, pk=pk)
    if sip.status not in ['DRAFT', 'DITOLAK']:
        messages.error(request, 'Hanya SIP berstatus Draft/Konsep atau Ditolak yang dapat diajukan.')
        return redirect('kendaraan:sip_detail', pk=pk)
    if not sip.file_konsep_pdf:
        messages.error(request, 'Generate Konsep PDF terlebih dahulu sebelum SIP diajukan.')
        return redirect('kendaraan:sip_detail', pk=pk)
    if not getattr(sip, 'file_tte_pengusul', None) or getattr(sip, 'status_tte_pengusul', 'BELUM') != 'SUDAH_TTE':
        messages.error(request, 'SIP belum dapat diajukan. Pengelola BMN wajib upload file Konsep SIP yang sudah TTE oleh pegawai pengusul terlebih dahulu.')
        return redirect('kendaraan:sip_detail', pk=pk)
    from .sip_penerbit import apply_snapshot_penerbit_sip_kendaraan, get_label_tujuan_pengajuan_sip_kendaraan
    apply_snapshot_penerbit_sip_kendaraan(sip, force=True)
    sip.save(update_fields=[
        'pejabat_penerbit_sip_kendaraan', 'nama_pejabat_penerbit_sip_kendaraan',
        'nip_pejabat_penerbit_sip_kendaraan', 'jabatan_pejabat_penerbit_sip_kendaraan',
        'pejabat_penandatangan', 'updated_at'
    ])
    if not sip.pejabat_penerbit_sip_kendaraan_id and not sip.nama_pejabat_penerbit_sip_kendaraan:
        messages.error(request, 'Pejabat penerbit SIP Kendaraan belum dikonfigurasi pada Master Unit Kerja. Silakan lengkapi pejabat penerbit terlebih dahulu.')
        return redirect('kendaraan:sip_detail', pk=pk)
    # Pengelola BMN hanya mengajukan data. Konsep/final PDF dibuat oleh pejabat penerbit.
    sip.status = 'DIAJUKAN'
    sip.tanggal_pengajuan = timezone.now()
    sip.catatan_penolakan = ''
    sip.save(update_fields=['status', 'tanggal_pengajuan', 'catatan_penolakan', 'updated_at'])
    messages.success(request, f'SIP Kendaraan berhasil diajukan kepada {get_label_tujuan_pengajuan_sip_kendaraan(sip)}.')
    return redirect('kendaraan:sip_detail', pk=pk)


# Alias lama agar URL lama tidak error, tetapi alurnya kini ke Kepala Biro Umum.
sip_ajukan_sekjen = sip_ajukan_kabiro


@login_required
@require_POST
def sip_setujui_kabiro(request, pk):
    if is_pengelola_bmn(request.user) and not is_admin_system(request.user):
        messages.error(request, 'Pengelola BMN tidak dapat menyetujui SIP Kendaraan.')
        return redirect('kendaraan:sip_detail', pk=pk)
    if not can_approve_sip_kendaraan_object(request.user, get_object_or_404(SIPKendaraan, pk=pk)):
        messages.error(request, 'Anda bukan pejabat penerbit SIP Kendaraan untuk unit kerja ini.')
        return redirect('kendaraan:sip_detail', pk=pk)
    sip = get_object_or_404(SIPKendaraan, pk=pk)
    if sip.status != 'DIAJUKAN':
        messages.error(request, 'Hanya SIP berstatus Diajukan yang dapat disetujui.')
        return redirect('kendaraan:sip_detail', pk=pk)
    # Pejabat penerbit cukup menyetujui atau menolak usulan.
    # Sesuai aturan proses bisnis terakhir: setelah pejabat klik Setujui SIP,
    # status langsung menjadi TERBIT. Pejabat tidak generate ulang PDF dan
    # tidak upload ulang dokumen; file PDF TTE pengusul dipakai sebagai dokumen
    # final terakhir yang dipreview pada Detail SIP Kendaraan.
    now = timezone.now()
    sip.status = 'TERBIT'
    sip.tanggal_persetujuan = now
    sip.disetujui_oleh = request.user
    sip.catatan_penolakan = ''

    update_fields = ['status', 'tanggal_persetujuan', 'disetujui_oleh', 'catatan_penolakan', 'updated_at']

    # Status langsung TERBIT, tetapi dokumen final pejabat belum dianggap lengkap
    # sampai pejabat penerbit mengupload file SIP yang sudah TTE Kepala Biro/
    # Sekretaris/Kepala Sentra/Kepala Balai. File TTE pengusul tetap disimpan
    # sebagai dokumen usulan, bukan sebagai final pejabat.
    if hasattr(sip, 'status_tte'):
        sip.status_tte = 'MENUNGGU_TTE'
        update_fields.append('status_tte')
    if hasattr(sip, 'tanggal_tte'):
        sip.tanggal_tte = None
        update_fields.append('tanggal_tte')
    if hasattr(sip, 'catatan_tte'):
        sip.catatan_tte = 'SIP Kendaraan sudah disetujui dan berstatus Terbit. Menunggu upload SIP final yang sudah TTE pejabat penerbit.'
        update_fields.append('catatan_tte')

    sip.save(update_fields=list(dict.fromkeys(update_fields)))
    messages.success(request, 'SIP Kendaraan disetujui dan status langsung menjadi Terbit. Silakan upload file SIP final yang sudah TTE pejabat penerbit.')
    return redirect('kendaraan:sip_detail', pk=pk)


sip_setujui_sekjen = sip_setujui_kabiro


@login_required
@require_POST
def sip_tolak_kabiro(request, pk):
    if is_pengelola_bmn(request.user) and not is_admin_system(request.user):
        messages.error(request, 'Pengelola BMN tidak dapat menolak SIP Kendaraan.')
        return redirect('kendaraan:sip_detail', pk=pk)
    if not can_approve_sip_kendaraan_object(request.user, get_object_or_404(SIPKendaraan, pk=pk)):
        messages.error(request, 'Anda bukan pejabat penerbit SIP Kendaraan untuk unit kerja ini.')
        return redirect('kendaraan:sip_detail', pk=pk)
    sip = get_object_or_404(SIPKendaraan, pk=pk)
    catatan = (request.POST.get('catatan_penolakan') or '').strip()
    if not catatan:
        messages.error(request, 'Catatan penolakan wajib diisi.')
        return redirect('kendaraan:sip_detail', pk=pk)
    if sip.status != 'DIAJUKAN':
        messages.error(request, 'Hanya SIP berstatus Diajukan yang dapat ditolak.')
        return redirect('kendaraan:sip_detail', pk=pk)
    sip.status = 'DITOLAK'
    sip.catatan_penolakan = catatan
    sip.tanggal_persetujuan = timezone.now()
    sip.disetujui_oleh = request.user
    sip.save(update_fields=['status', 'catatan_penolakan', 'tanggal_persetujuan', 'disetujui_oleh', 'updated_at'])
    messages.warning(request, 'SIP Kendaraan ditolak pejabat penerbit dan dikembalikan untuk perbaikan.')
    return redirect('kendaraan:sip_detail', pk=pk)


sip_tolak_sekjen = sip_tolak_kabiro


@login_required
@require_POST
def sip_upload_bsre_pdf(request, pk):
    sip = get_object_or_404(SIPKendaraan, pk=pk)
    if is_pengelola_bmn(request.user) and not is_admin_system(request.user):
        messages.error(request, 'Pengelola BMN tidak dapat upload PDF TTE BSrE. Upload dilakukan oleh pejabat penerbit.')
        return redirect('kendaraan:sip_detail', pk=pk)
    if not can_approve_sip_kendaraan_object(request.user, sip):
        messages.error(request, 'Anda bukan pejabat penerbit SIP Kendaraan untuk unit kerja ini.')
        return redirect('kendaraan:sip_detail', pk=pk)
    if sip.status != 'TERBIT':
        messages.error(request, 'Upload SIP yang sudah TTE pejabat penerbit hanya dapat dilakukan setelah SIP disetujui dan status menjadi Terbit.')
        return redirect('kendaraan:sip_detail', pk=pk)

    form = SIPKendaraanBSREUploadForm(request.POST, request.FILES, instance=sip)
    if not form.is_valid():
        for field_errors in form.errors.values():
            for err in field_errors:
                messages.error(request, err)
        return redirect('kendaraan:sip_detail', pk=pk)

    sip = form.save(commit=False)
    # Simpan juga ke dokumen_sip agar preview/menu lama tetap membaca file final.
    if sip.file_signed_pdf:
        sip.dokumen_sip = sip.file_signed_pdf
    sip.status = 'TERBIT'
    sip.status_tte = 'SUDAH_TTE'
    sip.tanggal_tte = timezone.now()
    sip.catatan_tte = 'SIP Kendaraan final yang sudah TTE Kepala Biro/Sekretaris/Kepala Sentra/Kepala Balai telah diupload oleh pejabat penerbit.'
    sip.save(update_fields=['file_signed_pdf', 'dokumen_sip', 'status', 'status_tte', 'tanggal_tte', 'catatan_tte', 'updated_at'])
    messages.success(request, 'SIP Kendaraan final yang sudah TTE pejabat penerbit berhasil diupload.')
    return redirect('kendaraan:sip_detail', pk=pk)


class KepalaBiroUmumSIPKendaraanListView(KepalaBiroUmumRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin, ListView):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    template_name = 'kendaraan/sekjen_sip_list.html'
    paginate_by = 15
    select_related = ['kendaraan', 'pegawai', 'kendaraan__unit_kerja', 'pegawai__unit_kerja']
    search_fields = [
        ('nomor_sip', 'Nomor SIP'),
        ('kendaraan__nomor_polisi', 'Nomor Polisi'),
        ('pegawai__nama', 'Nama Pegawai'),
        ('pegawai__nip', 'NIP Pegawai'),
        ('pegawai__jabatan', 'Jabatan Pegawai'),
        ('status', 'Status SIP'),
    ]

    def get_queryset(self):
        # Jangan memakai scope global Biro Umum untuk daftar persetujuan,
        # karena Kepala Biro Umum hanya boleh melihat SIP dari unit di bawah Setjen.
        # Pengajuan dari Pengelola BMN muncul di sini setelah status DIAJUKAN.
        from .sip_penerbit import get_sip_kendaraan_approval_unit_ids_for_user, _is_setjen_related_unit
        from core.access import get_user_pegawai

        user = self.request.user
        qs = SIPKendaraan.objects.select_related(*self.select_related)
        qs = qs.filter(status__in=['DIAJUKAN', 'DISETUJUI', 'DITOLAK', 'MENUNGGU_TTE', 'TERBIT'])

        unit_ids = get_sip_kendaraan_approval_unit_ids_for_user(user)
        if unit_ids is None:
            scoped = qs
        elif not unit_ids:
            scoped = qs.none()
        else:
            base_filter = Q(kendaraan__unit_kerja_id__in=unit_ids) | Q(pegawai__unit_kerja_id__in=unit_ids)

            # Untuk pejabat penerbit selain Kepala Biro Umum, tambahkan juga data yang
            # snapshot pejabat penerbitnya menunjuk langsung ke pegawai user tersebut.
            # Kepala Biro Umum tetap dibatasi ke unit Setjen saja.
            role_names = set(user.groups.values_list('name', flat=True))
            if 'Kepala Biro Umum' not in role_names:
                pegawai_user = get_user_pegawai(user)
                if pegawai_user:
                    base_filter |= Q(pejabat_penerbit_sip_kendaraan=pegawai_user)

            scoped = qs.filter(base_filter).distinct()

        scoped = _apply_search_filter(self.request, scoped, self.search_fields)
        return scoped.order_by('-tanggal_pengajuan', '-tanggal_sip')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['approval_title'] = 'Persetujuan Pejabat Penerbit SIP Kendaraan'
        return ctx


# Alias class lama agar name URL lama tetap kompatibel bila masih dipakai.
SekjenSIPKendaraanListView = KepalaBiroUmumSIPKendaraanListView


# =============================================================
# Export daftar/transaksi Kendaraan (PDF, Excel, CSV)
# =============================================================
def _sip_kendaraan_columns():
    return [
        ('No', '__no__'),
        ('Nomor SIP', 'nomor_sip'),
        ('Tanggal SIP', 'tanggal_sip'),
        ('Nomor Polisi', 'kendaraan__nomor_polisi'),
        ('Kendaraan', 'kendaraan'),
        ('Pemegang/Pegawai', 'pegawai__nama'),
        ('NIP', 'pegawai__nip'),
        ('Unit Kerja Pegawai', 'pegawai__unit_kerja__nama_unit'),
        ('Periode Mulai', 'tanggal_mulai'),
        ('Periode Akhir', 'tanggal_akhir'),
        ('Masa Berlaku', lambda o: getattr(o, 'masa_berlaku_display', '') or ''),
        ('Jenis Pemakaian', 'display:jenis_pemakaian'),
        ('Tujuan', 'tujuan_pemakaian'),
        ('Lokasi Penggunaan', 'lokasi_penggunaan'),
        ('Status', 'display:status'),
        ('Tanggal Pengajuan', 'tanggal_pengajuan'),
        ('Tanggal Persetujuan', 'tanggal_persetujuan'),
        ('Catatan', 'catatan'),
    ]


def _service_kendaraan_columns():
    return [
        ('No', '__no__'),
        ('Tanggal Service', 'tanggal_service'),
        ('Nomor Polisi', 'kendaraan__nomor_polisi'),
        ('Kendaraan', 'kendaraan'),
        ('Unit Kerja', 'kendaraan__unit_kerja__nama_unit'),
        ('Jenis Service', 'display:jenis_service'),
        ('Kilometer', 'kilometer'),
        ('Bengkel', 'bengkel'),
        ('Uraian Pekerjaan', 'uraian_pekerjaan'),
        ('Sparepart Diganti', 'sparepart_diganti'),
        ('Biaya Jasa', 'biaya_jasa'),
        ('Biaya Sparepart', 'biaya_sparepart'),
        ('Total Biaya', 'total_biaya'),
        ('Kondisi Sebelum', 'display:kondisi_sebelum'),
        ('Kondisi Sesudah', 'display:kondisi_sesudah'),
        ('Petugas', 'dicatat_oleh__username'),
    ]


def _kondisi_kendaraan_columns():
    return [
        ('No', '__no__'),
        ('Tanggal', 'tanggal'),
        ('Nomor Polisi', 'kendaraan__nomor_polisi'),
        ('Kendaraan', 'kendaraan'),
        ('Unit Kerja', 'kendaraan__unit_kerja__nama_unit'),
        ('Kondisi', 'display:kondisi'),
        ('Uraian Kondisi', 'uraian_kondisi'),
        ('Petugas', 'dicatat_oleh__username'),
    ]


@login_required
def export_sip_kendaraan(request, fmt):
    qs = scope_queryset_by_user(
        SIPKendaraan.objects.select_related('kendaraan', 'pegawai', 'kendaraan__unit_kerja', 'pegawai__unit_kerja'),
        request.user,
        'sip_kendaraan',
    )
    qs = apply_search_filter(qs, request, SIPKendaraanListView.search_fields)
    return export_queryset(request, qs, fmt, 'transaksi_sip_kendaraan', 'Daftar SIP Kendaraan', _sip_kendaraan_columns(), order_by=['-tanggal_sip', '-id'])


@login_required
def export_persetujuan_sip_kendaraan(request, fmt):
    if not can_approve_sip_kendaraan(request.user):
        raise PermissionDenied('Anda tidak memiliki hak akses export persetujuan SIP Kendaraan.')
    qs = SIPKendaraan.objects.select_related('kendaraan', 'pegawai', 'kendaraan__unit_kerja', 'pegawai__unit_kerja').filter(status__in=['DIAJUKAN', 'DISETUJUI', 'DITOLAK', 'TERBIT', 'AKTIF'])
    qs = apply_search_filter(qs, request, SIPKendaraanListView.search_fields)
    return export_queryset(request, qs, fmt, 'persetujuan_sip_kendaraan', 'Persetujuan SIP Kendaraan', _sip_kendaraan_columns(), order_by=['-tanggal_pengajuan', '-tanggal_sip', '-id'])


@login_required
def export_service_kendaraan(request, fmt):
    qs = scope_queryset_by_user(
        ServiceKendaraan.objects.select_related('kendaraan', 'kendaraan__unit_kerja', 'dicatat_oleh'),
        request.user,
        'service_kendaraan',
    )
    qs = apply_search_filter(qs, request, ServiceKendaraanListView.search_fields)
    return export_queryset(request, qs, fmt, 'transaksi_service_kendaraan', 'Daftar Service Kendaraan', _service_kendaraan_columns(), order_by=['-tanggal_service', '-id'])


@login_required
def export_kondisi_kendaraan(request, fmt):
    qs = scope_queryset_by_user(
        RiwayatKondisiKendaraan.objects.select_related('kendaraan', 'kendaraan__unit_kerja', 'dicatat_oleh'),
        request.user,
        'kondisi_kendaraan',
    )
    qs = apply_search_filter(qs, request, RiwayatKondisiListView.search_fields)
    return export_queryset(request, qs, fmt, 'transaksi_riwayat_kondisi_kendaraan', 'Riwayat Kondisi Kendaraan', _kondisi_kendaraan_columns(), order_by=['-tanggal', '-id'])
