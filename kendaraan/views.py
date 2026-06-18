import json

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView

from core.roles import BMNRequiredMixin, MaintenanceRequiredMixin, VehicleViewRequiredMixin, SIPEditRequiredMixin
from core.listing import SearchListMixin
from core.detail import GenericDetailMixin
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Tombol Teruskan ke Pejabat Penerbit ditampilkan pada Daftar SIP
        # untuk Pengelola BMN/Admin System selama status masih Draft atau Ditolak.
        # Proses submit tetap divalidasi ulang di view sip_ajukan_kabiro.
        ctx['can_submit_sip_kendaraan_from_list'] = can_manage_sip(self.request.user)
        ctx['submit_sip_kendaraan_button_label'] = 'Teruskan'
        ctx['hide_status_aktif_for_pengelola_bmn'] = is_pengelola_bmn(self.request.user) and not is_admin_system(self.request.user)
        return ctx


def _sip_kendaraan_form_context(obj=None):
    kendaraan_qs = Kendaraan.objects.select_related('unit_kerja', 'pejabat_penandatangan_sip').all()
    kendaraan_master_map = {}
    for k in kendaraan_qs:
        try:
            jenis_display = k.get_jenis_kendaraan_display()
        except Exception:
            jenis_display = k.jenis_kendaraan or ''
        pejabat = getattr(k, 'pejabat_penandatangan_sip', None)
        pejabat_display = ''
        pejabat_id = ''
        pejabat_nama = ''
        pejabat_nip = ''
        pejabat_jabatan = ''
        if pejabat:
            pejabat_id = str(getattr(pejabat, 'pk', '') or '')
            pejabat_nama = getattr(pejabat, 'nama', '') or ''
            pejabat_nip = getattr(pejabat, 'nip', '') or ''
            pejabat_jabatan = getattr(pejabat, 'jabatan', '') or 'Pejabat Penandatangan SIP Kendaraan'
            pejabat_display = f'{pejabat_nama} - {pejabat_nip} ({pejabat_jabatan})'
        kendaraan_master_map[str(k.pk)] = {
            'jenis_kendaraan': jenis_display or '',
            'jenis_kendaraan_value': k.jenis_kendaraan or '',
            'kode_barang': k.kode_barang or '',
            'nup': k.nup or '',
            'nomor_polisi': k.nomor_polisi or '',
            'merek_tipe': f"{k.merek or ''} {k.tipe or ''}".strip(),
            'unit_kerja': getattr(k.unit_kerja, 'nama_unit', '') or '',
            'pejabat_penandatangan': pejabat_display,
            'pejabat_penandatangan_id': pejabat_id,
            'pejabat_penandatangan_nama': pejabat_nama,
            'pejabat_penandatangan_nip': pejabat_nip,
            'pejabat_penandatangan_jabatan': pejabat_jabatan,
        }

    preview_docs = []
    if obj:
        def add_doc(label, f):
            if not f:
                return
            try:
                preview_docs.append({'label': label, 'url': f.url, 'is_pdf': str(f.name).lower().endswith('.pdf')})
            except Exception:
                pass
        add_doc('Preview Konsep PDF SIP Kendaraan', getattr(obj, 'file_konsep_pdf', None))
        add_doc('Preview SIP Final TTE Pejabat Penerbit', getattr(obj, 'file_signed_pdf', None) or getattr(obj, 'dokumen_sip', None))

    return {
        'kendaraan_master_json': json.dumps(kendaraan_master_map),
        'sip_form_preview_docs': preview_docs,
    }


class SIPKendaraanCreateView(BMNRequiredMixin, UnitScopedFormMixin, CreateView):
    model = SIPKendaraan
    form_class = SIPKendaraanForm
    template_name = 'kendaraan/sip_form.html'
    success_url = reverse_lazy('kendaraan:sip_list')

    def form_valid(self, form):
        # Pengelola BMN mengisi data SIP lalu menekan Buat/Generate SIP Kendaraan.
        # Setelah tersimpan, sistem langsung membuat konsep PDF untuk dipreview.
        form.instance.dibuat_oleh = self.request.user
        form.instance.status = 'DRAFT'
        if form.instance.kendaraan_id:
            form.instance.jenis_pemakaian = form.instance.kendaraan.jenis_kendaraan
        response = super().form_valid(form)
        try:
            generate_sip_kendaraan_pdf(self.object, concept=True)
            messages.success(self.request, 'SIP Kendaraan berhasil dibuat dan konsep PDF otomatis digenerate. Silakan cek preview PDF di bawah halaman detail, lalu ajukan ke pejabat penerbit.')
        except Exception as exc:
            messages.warning(self.request, f'SIP Kendaraan berhasil dibuat, tetapi konsep PDF belum berhasil digenerate: {exc}')
        return response

    def get_success_url(self):
        return reverse('kendaraan:sip_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_sip_kendaraan_form_context(self.object if hasattr(self, 'object') else None))
        ctx['submit_label'] = 'Buat / Generate SIP Kendaraan'
        return ctx


class SIPKendaraanUpdateView(SIPEditRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'sip_kendaraan'
    model = SIPKendaraan
    form_class = SIPKendaraanForm
    template_name = 'kendaraan/sip_form.html'
    success_url = reverse_lazy('kendaraan:sip_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status not in ['DRAFT', 'DITOLAK', 'DIAJUKAN', 'TERBIT'] and not request.user.is_superuser:
            messages.error(request, 'SIP Kendaraan hanya dapat diedit saat berstatus Draft/Konsep, Diajukan, Ditolak, atau Terbit.')
            return redirect('kendaraan:sip_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Jika revisi dari status Ditolak, kembalikan menjadi Draft/Konsep.
        if form.instance.status == 'DITOLAK':
            form.instance.status = 'DRAFT'
        if form.instance.kendaraan_id:
            form.instance.jenis_pemakaian = form.instance.kendaraan.jenis_kendaraan
        response = super().form_valid(form)
        try:
            generate_sip_kendaraan_pdf(self.object, concept=True)
            messages.success(self.request, 'Data SIP Kendaraan berhasil diperbarui dan konsep PDF otomatis digenerate ulang.')
        except Exception as exc:
            messages.warning(self.request, f'Data berhasil diperbarui, tetapi konsep PDF belum berhasil digenerate ulang: {exc}')
        return response

    def get_success_url(self):
        return reverse('kendaraan:sip_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_sip_kendaraan_form_context(self.object))
        ctx['submit_label'] = 'Simpan / Generate Ulang SIP Kendaraan'
        return ctx


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
            add_approval_doc('Preview SIP Kendaraan Final TTE', final_pdf)
        elif pengusul_pdf:
            add_approval_doc('Preview SIP Kendaraan TTE Pegawai Pengusul', pengusul_pdf)
        elif konsep_pdf:
            add_approval_doc('Preview Konsep PDF SIP Kendaraan', konsep_pdf)
        user = self.request.user
        from .sip_penerbit import get_label_tujuan_pengajuan_sip_kendaraan
        can_edit_draft = obj.status in ['DRAFT', 'DIAJUKAN', 'TERBIT']
        is_bmn_operator = (is_pengelola_bmn(user) or is_admin_system(user))

        # Pengelola BMN tetap sebagai pengusul, tetapi sesuai aturan koreksi terakhir
        # pada detail SIP Kendaraan tombol Edit, Hapus, dan Generate Konsep PDF tetap tersedia
        # selama status masih belum final/dapat direvisi. Upload PDF TTE tetap hanya untuk pejabat penerbit.
        # Tombol/fitur Setujui SIP dan Tolak SIP harus tampil pada halaman Detail
        # untuk Admin System dan pejabat penerbit/Kepala Unit Kerja-Satker yang berwenang
        # saat status SIP masih DIAJUKAN. Pengelola BMN murni tetap tidak boleh menyetujui.
        is_pengelola_bmn_only = is_pengelola_bmn(user) and not is_admin_system(user)
        can_approve_obj = (not is_pengelola_bmn_only) and can_approve_sip_kendaraan_object(user, obj)
        can_generate_concept_as_bmn = is_bmn_operator and obj.status in ['DRAFT', 'DITOLAK', 'DIAJUKAN']

        # Preview SIP Kendaraan dikelola melalui approval_docs agar hanya satu versi dokumen
        # yang muncul sesuai tahap proses. Hindari duplikasi dari preview dokumen_sip generic.
        ctx['dokumen_sip_url'] = None
        ctx['dokumen_sip_is_pdf'] = False

        ctx['sip_service_history'] = obj.kendaraan.service.all().order_by('-tanggal_service', '-created_at')[:10] if getattr(obj, 'kendaraan_id', None) else []

        ctx.update({
            'approval_docs': approval_docs,
            # Generate konsep PDF hanya untuk Pengelola BMN sebagai pengusul.
            # Pejabat penerbit cukup melakukan Setujui/Tolak dan tidak generate ulang PDF.
            'can_generate_concept_pdf': can_generate_concept_as_bmn,
            # Tampilkan form upload TTE calon pemegang untuk Pengelola BMN selama status belum final.
            # Gunakan status_upper agar data lama dengan status 'Draft', 'draft', atau variasi label lain tetap terbaca.
            'can_upload_tte_pengusul': False,
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

        # Tombol Edit tetap ada untuk Pengelola BMN/Admin pada status DRAFT, DIAJUKAN, dan TERBIT.
        # Status lain disembunyikan dari edit sesuai permintaan.
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
    messages.success(request, 'Konsep/Draft PDF SIP Kendaraan berhasil dibuat. Preview PDF tampil di bawah halaman detail. Selanjutnya ajukan ke pejabat penerbit untuk persetujuan.')
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
    # Pengelola BMN mengajukan konsep PDF yang sudah dibuat ke pejabat penerbit.
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
    # Pejabat penerbit/Kepala Unit Kerja-Satker menyetujui usulan melalui menu Review.
    # Form review menyediakan keterangan persetujuan agar keputusan pejabat terdokumentasi.
    now = timezone.now()
    keterangan_persetujuan = (request.POST.get('keterangan_persetujuan') or request.POST.get('keterangan') or '').strip()
    sip.status = 'TERBIT'
    sip.tanggal_persetujuan = now
    sip.disetujui_oleh = request.user
    sip.catatan_penolakan = ''
    if keterangan_persetujuan:
        sip.catatan = keterangan_persetujuan

    update_fields = ['status', 'tanggal_persetujuan', 'disetujui_oleh', 'catatan_penolakan', 'updated_at']
    if keterangan_persetujuan:
        update_fields.append('catatan')

    # Status langsung TERBIT, tetapi dokumen final pejabat belum dianggap lengkap
    # sampai pejabat penerbit mengupload file SIP yang sudah TTE Kepala Biro/
    # Sekretaris/Kepala Sentra/Kepala Balai. File TTE pengusul tetap disimpan
    # sebagai dokumen usulan, bukan sebagai final pejabat.
    if hasattr(sip, 'status_tte'):
        sip.status_tte = 'SIAP_TTE'
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
    alasan = (request.POST.get('alasan_penolakan') or request.POST.get('catatan_penolakan') or '').strip()
    keterangan = (request.POST.get('keterangan_penolakan') or request.POST.get('keterangan') or '').strip()
    if not alasan:
        messages.error(request, 'Alasan penolakan wajib diisi.')
        return redirect('kendaraan:sip_detail', pk=pk)
    catatan = alasan
    if keterangan:
        catatan = f'Alasan: {alasan}\nKeterangan: {keterangan}'
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
        messages.error(request, 'Pengelola BMN tidak dapat upload PDF TTE. Upload dilakukan oleh pejabat penerbit.')
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


def _stringify(value):
    if value is None:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime('%d/%m/%Y')
    return str(value)


def _sip_kendaraan_export_rows(qs):
    rows = []
    for o in qs.select_related('kendaraan', 'pegawai', 'kendaraan__unit_kerja'):
        rows.append([
            o.nomor_sip,
            o.tanggal_sip,
            getattr(o.kendaraan, 'kode_kendaraan', '') if o.kendaraan_id else '',
            getattr(o.kendaraan, 'nomor_polisi', '') if o.kendaraan_id else '',
            getattr(o.kendaraan, 'jenis_kendaraan', '') if o.kendaraan_id else '',
            getattr(o.kendaraan, 'kode_barang', '') if o.kendaraan_id else '',
            getattr(o.kendaraan, 'nup', '') if o.kendaraan_id else '',
            getattr(o.kendaraan.unit_kerja, 'nama_unit', '') if o.kendaraan_id and o.kendaraan.unit_kerja_id else '',
            getattr(o.pegawai, 'nama', '') if o.pegawai_id else '',
            getattr(o.pegawai, 'nip', '') if o.pegawai_id else '',
            o.tanggal_mulai,
            o.tanggal_akhir,
            o.get_status_display(),
            o.status_aktif_display,
            o.pejabat_penandatangan or o.jabatan_pejabat_penerbit_sip_kendaraan or '',
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
    qs = scope_queryset_by_user(SIPKendaraan.objects.all(), request.user, 'sip_kendaraan')
    qs = _apply_search_filter(request, qs, SIPKendaraanListView.search_fields).order_by('-tanggal_sip')
    headers = ['Nomor SIP', 'Tanggal SIP', 'Kode Register', 'Nomor Polisi', 'Jenis Kendaraan', 'Kode Barang', 'NUP', 'Unit Kerja', 'Pengguna', 'NIP', 'Tanggal Mulai', 'Tanggal Akhir', 'Status Proses', 'Status Aktif/Non Aktif', 'Pejabat Penerbit']
    return _export_rows_response(fmt, 'export_sip_kendaraan', 'Export SIP Kendaraan', headers, _sip_kendaraan_export_rows(qs))


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
