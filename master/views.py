from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models.deletion import ProtectedError
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, FormView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from core.roles import BMNRequiredMixin, VehicleViewRequiredMixin, can_manage_master
from core.forms import ImportFileForm
from core.import_utils import read_tabular_upload, pick, to_int, to_decimal, to_date, normalize_choice
from core.constants import KONDISI_ASET, STATUS_PEMANFAATAN_KENDARAAN, STATUS_PEMANFAATAN_RUMAH, JENIS_KENDARAAN_CHOICES
from core.listing import SearchListMixin
from core.detail import GenericDetailMixin
from core.access import UnitScopedQuerysetMixin, UnitScopedFormMixin, BiroUmumOnlyMixin, scope_queryset_by_user, is_biro_umum_user, get_user_unit_kerja
from .models import (
    UnitKerja,
    Pegawai,
    Kendaraan,
    RumahDinas,
    FotoKendaraan,
    FotoRumahDinas,
)
from .forms import UnitKerjaForm, PegawaiForm, KendaraanForm, RumahDinasForm


class SafeDeleteMixin:
    """DeleteView helper untuk tombol hapus dengan pesan dan proteksi relasi."""
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


class UnitKerjaListView(BMNRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'unit'
    model = UnitKerja
    template_name = 'master/unitkerja_list.html'
    search_fields = [
        ('nama_unit', 'Nama Unit Kerja'),
        ('keterangan', 'Keterangan'),
    ]


class UnitKerjaCreateView(BMNRequiredMixin, BiroUmumOnlyMixin, UnitScopedFormMixin, CreateView):
    model = UnitKerja
    form_class = UnitKerjaForm
    template_name = 'master/form.html'
    success_url = reverse_lazy('master:unitkerja_list')


class UnitKerjaUpdateView(BMNRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'unit'
    model = UnitKerja
    form_class = UnitKerjaForm
    template_name = 'master/form.html'
    success_url = reverse_lazy('master:unitkerja_list')


class UnitKerjaDetailView(BMNRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'unit'
    model = UnitKerja
    detail_title = 'Detail Unit Kerja'
    back_url_name = 'master:unitkerja_list'
    edit_url_name = 'master:unitkerja_update'
    delete_url_name = 'master:unitkerja_delete'


class UnitKerjaDeleteView(BMNRequiredMixin, BiroUmumOnlyMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'unit'
    model = UnitKerja
    success_url = reverse_lazy('master:unitkerja_list')
    success_message = 'Unit kerja berhasil dihapus.'
    protected_message = 'Unit kerja tidak dapat dihapus karena masih digunakan oleh pegawai/aset/transaksi.'


class PegawaiListView(BMNRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'pegawai'
    model = Pegawai
    template_name = 'master/pegawai_list.html'
    select_related = ['unit_kerja']
    search_fields = [
        ('nip', 'NIP'),
        ('nik', 'NIK'),
        ('nama', 'Nama Pegawai'),
        ('jabatan', 'Jabatan'),
        ('pangkat', 'Pangkat'),
        ('golongan', 'Golongan'),
        ('unit_kerja__nama_unit', 'Unit Kerja'),
        ('no_hp', 'No HP'),
        ('email', 'Email'),
        ('status_pegawai', 'Status Pegawai'),
    ]


class PegawaiCreateView(BMNRequiredMixin, UnitScopedFormMixin, CreateView):
    model = Pegawai
    form_class = PegawaiForm
    template_name = 'master/pegawai_form.html'
    success_url = reverse_lazy('master:pegawai_list')


class PegawaiUpdateView(BMNRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, UpdateView):
    scope_type = 'pegawai'
    model = Pegawai
    form_class = PegawaiForm
    template_name = 'master/pegawai_form.html'
    success_url = reverse_lazy('master:pegawai_list')


class PegawaiDetailView(BMNRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'pegawai'
    model = Pegawai
    detail_title = 'Detail Pegawai'
    back_url_name = 'master:pegawai_list'
    edit_url_name = 'master:pegawai_update'
    delete_url_name = 'master:pegawai_delete'


class PegawaiDeleteView(BMNRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'pegawai'
    model = Pegawai
    success_url = reverse_lazy('master:pegawai_list')
    success_message = 'Pegawai berhasil dihapus.'
    protected_message = 'Pegawai tidak dapat dihapus karena masih digunakan pada SIP/pengguna aset/transaksi.'


@login_required
@require_POST
def pegawai_foto_delete(request, pk):
    if not can_manage_master(request.user):
        messages.error(request, 'Anda tidak memiliki hak akses untuk menghapus foto pegawai.')
        return redirect('dashboard')

    pegawai = get_object_or_404(scope_queryset_by_user(Pegawai.objects.all(), request.user, 'pegawai'), pk=pk)

    if pegawai.foto:
        pegawai.foto.delete(save=False)
        pegawai.foto = None
        pegawai.save(update_fields=['foto', 'updated_at'])
        messages.success(request, 'Foto pegawai berhasil dihapus.')
    else:
        messages.info(request, 'Pegawai ini belum memiliki foto.')

    return redirect('master:pegawai_update', pk=pegawai.pk)


class KendaraanListView(VehicleViewRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'kendaraan'
    model = Kendaraan
    template_name = 'master/kendaraan_list.html'
    select_related = ['unit_kerja', 'pengguna']
    search_fields = [
        ('kode_kendaraan', 'Kode Kendaraan'),
        ('nomor_polisi', 'Nomor Polisi'),
        ('merek', 'Merek'),
        ('tipe', 'Tipe'),
        ('jenis_kendaraan', 'Jenis Kendaraan'),
        ('warna', 'Warna'),
        ('nomor_rangka', 'Nomor Rangka'),
        ('nomor_mesin', 'Nomor Mesin'),
        ('nomor_bpkb', 'Nomor BPKB'),
        ('nomor_stnk', 'Nomor STNK'),
        ('nup', 'NUP'),
        ('kode_barang', 'Kode Barang'),
        ('unit_kerja__nama_unit', 'Unit Kerja'),
        ('pengguna__nama', 'Nama Pengguna'),
        ('pengguna__nip', 'NIP Pengguna'),
        ('kondisi', 'Kondisi'),
        ('status_pemanfaatan', 'Status Pemanfaatan'),
    ]


class KendaraanPhotoMixin:
    template_name = 'master/kendaraan_form.html'
    success_url = reverse_lazy('master:kendaraan_list')

    def save_uploaded_photos(self, kendaraan):
        for foto in self.request.FILES.getlist('foto_kendaraan'):
            FotoKendaraan.objects.create(
                kendaraan=kendaraan,
                foto=foto,
                diupload_oleh=self.request.user if self.request.user.is_authenticated else None
            )

    def form_valid(self, form):
        response = super().form_valid(form)
        self.save_uploaded_photos(self.object)
        messages.success(self.request, 'Data kendaraan berhasil disimpan.')
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if getattr(self, 'object', None):
            ctx['foto_kendaraan_list'] = self.object.galeri_foto.all()
        else:
            ctx['foto_kendaraan_list'] = []

        return ctx


class KendaraanCreateView(BMNRequiredMixin, UnitScopedFormMixin, KendaraanPhotoMixin, CreateView):
    model = Kendaraan
    form_class = KendaraanForm


class KendaraanUpdateView(BMNRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, KendaraanPhotoMixin, UpdateView):
    scope_type = 'kendaraan'
    model = Kendaraan
    form_class = KendaraanForm


class KendaraanDetailView(VehicleViewRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'kendaraan'
    model = Kendaraan
    detail_title = 'Detail Kendaraan'
    back_url_name = 'master:kendaraan_list'
    edit_url_name = 'master:kendaraan_update'
    delete_url_name = 'master:kendaraan_delete'


class KendaraanDeleteView(BMNRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'kendaraan'
    model = Kendaraan
    success_url = reverse_lazy('master:kendaraan_list')
    success_message = 'Kendaraan berhasil dihapus.'
    protected_message = 'Kendaraan tidak dapat dihapus karena masih digunakan pada SIP/service/riwayat kondisi.'


@login_required
@require_POST
def kendaraan_foto_delete(request, pk):
    if not can_manage_master(request.user):
        messages.error(request, 'Anda tidak memiliki hak akses untuk menghapus foto kendaraan.')
        return redirect('dashboard')

    foto = get_object_or_404(FotoKendaraan.objects.filter(kendaraan__in=scope_queryset_by_user(Kendaraan.objects.all(), request.user, 'kendaraan')), pk=pk)
    kendaraan_id = foto.kendaraan_id
    foto.foto.delete(save=False)
    foto.delete()

    messages.success(request, 'Foto kendaraan berhasil dihapus.')
    return redirect('master:kendaraan_update', pk=kendaraan_id)


class RumahDinasListView(BMNRequiredMixin, UnitScopedQuerysetMixin, SearchListMixin):
    scope_type = 'rumah'
    model = RumahDinas
    template_name = 'master/rumah_list.html'
    search_fields = [
        ('kode_rumah', 'Kode Rumah'),
        ('nama_rumah', 'Nama Rumah'),
        ('jenis_rumah', 'Jenis Rumah'),
        ('alamat', 'Alamat'),
        ('provinsi', 'Provinsi'),
        ('kabupaten_kota', 'Kabupaten/Kota'),
        ('kecamatan', 'Kecamatan'),
        ('kelurahan', 'Kelurahan'),
        ('nup', 'NUP'),
        ('kode_barang', 'Kode Barang'),
        ('nomor_sertifikat', 'Nomor Sertifikat'),
        ('status_tanah', 'Status Tanah'),
        ('unit_kerja__nama_unit', 'Unit Kerja'),
        ('kondisi', 'Kondisi'),
        ('status_pemanfaatan', 'Status Pemanfaatan'),
    ]


class RumahDinasPhotoMixin:
    template_name = 'master/rumah_form.html'
    success_url = reverse_lazy('master:rumah_list')

    def save_uploaded_photos(self, rumah_dinas):
        for foto in self.request.FILES.getlist('foto_rumah_dinas'):
            FotoRumahDinas.objects.create(
                rumah_dinas=rumah_dinas,
                foto=foto,
                diupload_oleh=self.request.user if self.request.user.is_authenticated else None
            )

    def form_valid(self, form):
        response = super().form_valid(form)
        self.save_uploaded_photos(self.object)
        messages.success(self.request, 'Data rumah negara berhasil disimpan.')
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if getattr(self, 'object', None):
            ctx['foto_rumah_list'] = self.object.galeri_foto.all()
        else:
            ctx['foto_rumah_list'] = []

        return ctx


class RumahDinasCreateView(BMNRequiredMixin, BiroUmumOnlyMixin, UnitScopedFormMixin, RumahDinasPhotoMixin, CreateView):
    model = RumahDinas
    form_class = RumahDinasForm


class RumahDinasUpdateView(BMNRequiredMixin, UnitScopedQuerysetMixin, UnitScopedFormMixin, RumahDinasPhotoMixin, UpdateView):
    scope_type = 'rumah'
    model = RumahDinas
    form_class = RumahDinasForm


class RumahDinasDetailView(BMNRequiredMixin, UnitScopedQuerysetMixin, GenericDetailMixin, DetailView):
    scope_type = 'rumah'
    model = RumahDinas
    detail_title = 'Detail Rumah Negara'
    back_url_name = 'master:rumah_list'
    edit_url_name = 'master:rumah_update'
    delete_url_name = 'master:rumah_delete'


class RumahDinasDeleteView(BMNRequiredMixin, UnitScopedQuerysetMixin, SafeDeleteMixin, DeleteView):
    scope_type = 'rumah'
    model = RumahDinas
    success_url = reverse_lazy('master:rumah_list')
    success_message = 'Rumah negara berhasil dihapus.'
    protected_message = 'Rumah negara tidak dapat dihapus karena masih digunakan pada SIP/transaksi terkait.'


@login_required
@require_POST
def rumah_foto_delete(request, pk):
    if not can_manage_master(request.user):
        messages.error(request, 'Anda tidak memiliki hak akses untuk menghapus foto rumah negara.')
        return redirect('dashboard')

    foto = get_object_or_404(FotoRumahDinas.objects.filter(rumah_dinas__in=scope_queryset_by_user(RumahDinas.objects.all(), request.user, 'rumah')), pk=pk)
    rumah_id = foto.rumah_dinas_id
    foto.foto.delete(save=False)
    foto.delete()

    messages.success(request, 'Foto rumah negara berhasil dihapus.')
    return redirect('master:rumah_update', pk=rumah_id)


# =========================
# IMPORT EXCEL/CSV
# =========================

def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _json_or_redirect(request, ok, message, redirect_url, status=200):
    if _is_ajax(request):
        return JsonResponse({'ok': ok, 'message': message, 'redirect_url': str(redirect_url)}, status=status)
    if ok:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect(redirect_url)


def _get_or_create_unit(name, user):
    if not is_biro_umum_user(user):
        return get_user_unit_kerja(user)
    if not name:
        return None
    return UnitKerja.objects.get_or_create(nama_unit=str(name).strip())[0]


class BaseImportView(BMNRequiredMixin, FormView):
    form_class = ImportFileForm
    template_name = 'includes/import_form.html'
    title = 'Impor Data'
    description = ''
    back_url_name = None

    def get_success_url(self):
        return reverse_lazy(self.back_url_name)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'title': self.title, 'description': self.description, 'back_url': self.get_success_url()})
        return ctx

    def process_rows(self, rows):
        raise NotImplementedError

    def form_valid(self, form):
        try:
            rows = read_tabular_upload(form.cleaned_data['file'])
            created, updated, errors = self.process_rows(rows)
            msg = f'{self.title} selesai. Baru: {created}, Update: {updated}, Gagal: {errors}.'
            return _json_or_redirect(self.request, True, msg, self.get_success_url())
        except Exception as exc:
            return _json_or_redirect(self.request, False, str(exc), self.get_success_url(), status=400)

    def form_invalid(self, form):
        errors = []
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f'{field}: {error}')
        message = 'Form tidak valid. ' + '; '.join(errors)
        return _json_or_redirect(self.request, False, message, self.get_success_url(), status=400)


class PegawaiImportView(BaseImportView):
    title = 'Impor Pegawai'
    description = 'Kolom yang didukung: nip, nik, nama, jabatan, pangkat, golongan, unit_kerja, no_hp, email, alamat, status_pegawai.'
    back_url_name = 'master:pegawai_list'

    def process_rows(self, rows):
        created = updated = errors = 0
        for row in rows:
            nip = pick(row, 'nip')
            nama = pick(row, 'nama', 'nama_pegawai')
            if not nip or not nama:
                errors += 1; continue
            obj, is_created = Pegawai.objects.update_or_create(
                nip=str(nip),
                defaults={
                    'nik': pick(row, 'nik'), 'nama': nama, 'jabatan': pick(row, 'jabatan'),
                    'pangkat': pick(row, 'pangkat'), 'golongan': pick(row, 'golongan'),
                    'unit_kerja': _get_or_create_unit(pick(row, 'unit_kerja', 'satker'), self.request.user),
                    'no_hp': pick(row, 'no_hp', 'hp', 'telepon'), 'email': pick(row, 'email'),
                    'alamat': pick(row, 'alamat'), 'status_pegawai': pick(row, 'status_pegawai', 'status', default='Aktif'),
                })
            created += 1 if is_created else 0; updated += 0 if is_created else 1
        return created, updated, errors


class KendaraanImportView(BaseImportView):
    title = 'Impor Aset Kendaraan'
    description = 'Kolom yang didukung: kode_kendaraan, nomor_polisi, merek, tipe, jenis_kendaraan, tahun_pembuatan, tahun_perolehan, warna, nomor_rangka, nomor_mesin, nomor_bpkb, nomor_stnk, masa_berlaku_stnk, jatuh_tempo_pajak, nup, kode_barang, nilai_perolehan, unit_kerja, pengguna_nip, kondisi, status_pemanfaatan, kilometer_terakhir.'
    back_url_name = 'master:kendaraan_list'

    def process_rows(self, rows):
        created = updated = errors = 0
        for row in rows:
            kode = pick(row, 'kode_kendaraan', 'kode', 'nup')
            nopol = pick(row, 'nomor_polisi', 'nopol', 'plat_nomor')
            merek = pick(row, 'merek', 'merk', default='-')
            if not kode or not nopol:
                errors += 1; continue
            pengguna = None
            pengguna_nip = pick(row, 'pengguna_nip', 'nip_pengguna')
            if pengguna_nip:
                pengguna = Pegawai.objects.filter(nip__iexact=str(pengguna_nip)).first()
            obj, is_created = Kendaraan.objects.update_or_create(
                nomor_polisi=str(nopol).strip().upper(),
                defaults={
                    'kode_kendaraan': str(kode), 'merek': merek, 'tipe': pick(row, 'tipe'),
                    'jenis_kendaraan': normalize_choice(pick(row, 'jenis_kendaraan'), JENIS_KENDARAAN_CHOICES, None),
                    'tahun_pembuatan': to_int(pick(row, 'tahun_pembuatan')), 'tahun_perolehan': to_int(pick(row, 'tahun_perolehan')),
                    'warna': pick(row, 'warna'), 'nomor_rangka': pick(row, 'nomor_rangka'), 'nomor_mesin': pick(row, 'nomor_mesin'),
                    'nomor_bpkb': pick(row, 'nomor_bpkb'), 'nomor_stnk': pick(row, 'nomor_stnk'),
                    'masa_berlaku_stnk': to_date(pick(row, 'masa_berlaku_stnk')), 'jatuh_tempo_pajak': to_date(pick(row, 'jatuh_tempo_pajak')),
                    'nup': pick(row, 'nup'), 'kode_barang': pick(row, 'kode_barang'), 'nilai_perolehan': to_decimal(pick(row, 'nilai_perolehan', 'nilai'), 0),
                    'unit_kerja': _get_or_create_unit(pick(row, 'unit_kerja', 'satker'), self.request.user), 'pengguna': pengguna,
                    'kondisi': normalize_choice(pick(row, 'kondisi'), KONDISI_ASET, 'BAIK'),
                    'status_pemanfaatan': normalize_choice(pick(row, 'status_pemanfaatan', 'status'), STATUS_PEMANFAATAN_KENDARAAN, 'TERSEDIA'),
                    'kilometer_terakhir': to_int(pick(row, 'kilometer_terakhir', 'km'), 0) or 0,
                })
            created += 1 if is_created else 0; updated += 0 if is_created else 1
        return created, updated, errors


class RumahNegaraImportView(BaseImportView):
    title = 'Impor Aset Rumah Negara'
    description = 'Kolom yang didukung: kode_rumah, nama_rumah, jenis_rumah, alamat, provinsi, kabupaten_kota, kecamatan, kelurahan, latitude, longitude, luas_tanah, luas_bangunan, nup, kode_barang, nilai_perolehan, nomor_sertifikat, status_tanah, kondisi, status_pemanfaatan.'
    back_url_name = 'master:rumah_list'

    def process_rows(self, rows):
        created = updated = errors = 0
        for row in rows:
            kode = pick(row, 'kode_rumah', 'kode', 'nup')
            nama = pick(row, 'nama_rumah', 'nama', 'nama_aset', default=str(kode or ''))
            alamat = pick(row, 'alamat', default='-')
            if not kode:
                errors += 1; continue
            obj, is_created = RumahDinas.objects.update_or_create(
                kode_rumah=str(kode),
                defaults={
                    'nama_rumah': nama, 'jenis_rumah': pick(row, 'jenis_rumah'), 'alamat': alamat,
                    'provinsi': pick(row, 'provinsi'), 'kabupaten_kota': pick(row, 'kabupaten_kota','kabupaten','kota'),
                    'kecamatan': pick(row, 'kecamatan'), 'kelurahan': pick(row, 'kelurahan'),
                    'latitude': to_decimal(pick(row, 'latitude', 'lat'), None), 'longitude': to_decimal(pick(row, 'longitude','long','lng'), None),
                    'luas_tanah': to_decimal(pick(row, 'luas_tanah'), None), 'luas_bangunan': to_decimal(pick(row, 'luas_bangunan'), None),
                    'jumlah_kamar_tidur': to_int(pick(row, 'jumlah_kamar_tidur','kamar_tidur'), 0) or 0,
                    'jumlah_kamar_mandi': to_int(pick(row, 'jumlah_kamar_mandi','kamar_mandi'), 0) or 0,
                    'daya_listrik': pick(row, 'daya_listrik'), 'tahun_dibangun': to_int(pick(row, 'tahun_dibangun')),
                    'tahun_perolehan': to_int(pick(row, 'tahun_perolehan')), 'nup': pick(row, 'nup'), 'kode_barang': pick(row, 'kode_barang'),
                    'nilai_perolehan': to_decimal(pick(row, 'nilai_perolehan','nilai'), 0), 'unit_kerja': _get_or_create_unit(pick(row, 'unit_kerja', 'satker'), self.request.user),
                    'nomor_sertifikat': pick(row, 'nomor_sertifikat'),
                    'status_tanah': pick(row, 'status_tanah'), 'kondisi': normalize_choice(pick(row, 'kondisi'), KONDISI_ASET, 'BAIK'),
                    'status_pemanfaatan': normalize_choice(pick(row, 'status_pemanfaatan', 'status'), STATUS_PEMANFAATAN_RUMAH, 'KOSONG'),
                })
            created += 1 if is_created else 0; updated += 0 if is_created else 1
        return created, updated, errors
