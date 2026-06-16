import random

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from core.listing import SearchListMixin
from core.export_utils import apply_search_filter, export_queryset
from core.roles import AdminSystemRequiredMixin
from .models import LoginHistory, UserVisitCounter
from .forms import CaptchaLoginForm, RoleForm, UserCreateForm, UserUpdateForm, ProfileUpdateForm


def _generate_captcha(request):
    a = random.randint(2, 9)
    b = random.randint(1, 9)
    request.session['login_captcha_question'] = f'{a} + {b}'
    request.session['login_captcha_answer'] = str(a + b)
    request.session.modified = True


class SecureLoginView(LoginView):
    """Login SIKARIS dengan captcha sederhana tanpa OTP email."""
    template_name = 'accounts/login.html'
    authentication_form = CaptchaLoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            _generate_captcha(request)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Login berhasil.')
        return super().form_valid(form)

    def form_invalid(self, form):
        _generate_captcha(self.request)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['captcha_question'] = self.request.session.get('login_captcha_question', '')
        return ctx


class UserListView(AdminSystemRequiredMixin, SearchListMixin):
    model = get_user_model()
    template_name = 'accounts/user_list.html'
    ordering = ['username']
    search_fields = [
        ('username', 'Username'),
        ('email', 'Email'),
        ('first_name', 'Nama Depan'),
        ('last_name', 'Nama Belakang'),
        ('groups__name', 'Role'),
        ('profile__unit_kerja__nama_unit', 'Unit Kerja'),
    ]
    select_related = ['profile__unit_kerja']
    prefetch_related = ['groups']

    def get_queryset(self):
        return super().get_queryset().distinct()


class LoginHistoryListView(AdminSystemRequiredMixin, SearchListMixin):
    """Riwayat login seluruh user, hanya untuk Admin System."""
    model = LoginHistory
    template_name = 'accounts/login_history_list.html'
    ordering = ['-login_at']
    select_related = ['user', 'user__profile__unit_kerja']
    search_fields = [
        ('user__username', 'Username'),
        ('user__first_name', 'Nama Depan'),
        ('user__last_name', 'Nama Belakang'),
        ('user__email', 'Email'),
        ('user__profile__unit_kerja__nama_unit', 'Unit Kerja'),
        ('ip_address', 'IP Address'),
        ('user_agent', 'User Agent'),
    ]


class UserVisitCounterListView(AdminSystemRequiredMixin, SearchListMixin):
    """Counter kunjungan user, hanya untuk Admin System."""
    model = UserVisitCounter
    template_name = 'accounts/visit_counter_list.html'
    ordering = ['-total_kunjungan', 'user__username']
    select_related = ['user', 'user__profile__unit_kerja']
    search_fields = [
        ('user__username', 'Username'),
        ('user__first_name', 'Nama Depan'),
        ('user__last_name', 'Nama Belakang'),
        ('user__email', 'Email'),
        ('user__profile__unit_kerja__nama_unit', 'Unit Kerja'),
        ('last_path', 'Halaman Terakhir'),
        ('last_ip_address', 'IP Terakhir'),
    ]


class UserCreateView(AdminSystemRequiredMixin, CreateView):
    model = get_user_model()
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User berhasil ditambahkan.')
        return super().form_valid(form)


class UserUpdateView(AdminSystemRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User berhasil diperbarui.')
        return super().form_valid(form)


class UserDeleteView(AdminSystemRequiredMixin, DeleteView):
    model = get_user_model()
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.pk == request.user.pk:
            messages.error(request, 'User yang sedang login tidak boleh menghapus dirinya sendiri.')
            return redirect('user_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'User berhasil dihapus.')
        return super().form_valid(form)


class RoleListView(AdminSystemRequiredMixin, SearchListMixin):
    model = Group
    template_name = 'accounts/role_list.html'
    ordering = ['name']
    search_fields = [
        ('name', 'Nama Role'),
    ]


class RoleCreateView(AdminSystemRequiredMixin, CreateView):
    model = Group
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('role_list')

    def form_valid(self, form):
        messages.success(self.request, 'Role berhasil ditambahkan.')
        return super().form_valid(form)


class RoleUpdateView(AdminSystemRequiredMixin, UpdateView):
    model = Group
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('role_list')

    def form_valid(self, form):
        messages.success(self.request, 'Role berhasil diperbarui.')
        return super().form_valid(form)


class RoleDeleteView(AdminSystemRequiredMixin, DeleteView):
    model = Group
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('role_list')

    protected_roles = {'Admin System', 'Biro Umum', 'Kepala Biro Umum', 'Sekretaris Jenderal', 'Pengelola BMN', 'Pemeliharaan Kendaraan'}

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.name in self.protected_roles:
            messages.error(request, 'Role bawaan sistem tidak boleh dihapus.')
            return redirect('role_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Role berhasil dihapus.')
        return super().form_valid(form)


def _hak_akses_for_user(user):
    """Deskripsi role dan hak akses untuk ditampilkan pada Edit Profile."""
    role_names = list(user.groups.values_list('name', flat=True))
    if user.is_superuser and 'Superuser' not in role_names:
        role_names.insert(0, 'Superuser')

    akses_map = {
        'Superuser': [
            'Akses penuh seluruh fitur dan seluruh satker/unit kerja.',
            'Dapat mengelola user, role, master data, transaksi, laporan, dan konfigurasi aplikasi.',
        ],
        'Admin System': [
            'Akses penuh pengelolaan sistem dan seluruh data lintas unit kerja.',
            'Dapat mengelola user, role, master data, transaksi, laporan, dan konfigurasi aplikasi.',
        ],
        'Biro Umum': [
            'Dapat melihat dan mengelola data lintas satker sesuai kewenangan Biro Umum.',
            'Dapat mengelola master data, penghapusan BMN, PSP BMN, laporan, dan konfigurasi unit kerja.',
        ],
        'Pengelola BMN': [
            'Dapat mengelola master pegawai, kendaraan, dan rumah negara sesuai scope unit kerja/satker.',
            'Dapat membuat Draft/Konsep SIP Kendaraan lalu mengajukan ke pejabat penerbit.',
            'Tidak dapat menyetujui/menolak SIP dan tidak mengupload dokumen SIP final/TTE BSrE.',
        ],
        'Pemeliharaan Kendaraan': [
            'Dapat mengelola data service/pemeliharaan kendaraan sesuai kewenangan.',
            'Tidak mendapat menu master pegawai, rumah negara, SIP Rumah Negara, Penghapusan, PSP, dan Export Rumah Negara.',
        ],
        'Kepala Biro Umum': [
            'Dapat mereview pengajuan SIP Kendaraan dari unit di bawah Sekretariat Jenderal.',
            'Dapat generate konsep/final PDF SIP Kendaraan, menyetujui/menolak, dan mengupload SIP final yang sudah TTE BSrE.',
            'Tidak menggunakan menu Daftar SIP Kendaraan/Rumah Negara umum.',
        ],
        'Sekretaris Ditjen': [
            'Dapat mereview pengajuan SIP Kendaraan dari unit di bawah Direktorat Jenderal terkait.',
            'Dapat generate konsep/final PDF SIP Kendaraan, menyetujui/menolak, dan mengupload SIP final yang sudah TTE BSrE.',
        ],
        'Sekretaris Eselon I': [
            'Dapat mereview pengajuan SIP Kendaraan dari unit di bawah Eselon I terkait.',
            'Dapat generate konsep/final PDF SIP Kendaraan, menyetujui/menolak, dan mengupload SIP final yang sudah TTE BSrE.',
        ],
        'Sekretaris UKE II': [
            'Dapat mereview pengajuan SIP Kendaraan sesuai kewenangan UKE II.',
            'Dapat generate konsep/final PDF SIP Kendaraan, menyetujui/menolak, dan mengupload SIP final yang sudah TTE BSrE.',
        ],
        'Kepala Sentra': [
            'Dapat mereview pengajuan SIP Kendaraan dari Sentra masing-masing.',
            'Dapat generate konsep/final PDF SIP Kendaraan, menyetujui/menolak, dan mengupload SIP final yang sudah TTE BSrE.',
        ],
        'Kepala Balai': [
            'Dapat mereview pengajuan SIP Kendaraan dari Balai masing-masing.',
            'Dapat generate konsep/final PDF SIP Kendaraan, menyetujui/menolak, dan mengupload SIP final yang sudah TTE BSrE.',
        ],
        'Pejabat Penerbit SIP': [
            'Dapat mereview pengajuan SIP Kendaraan sesuai konfigurasi pejabat penerbit pada Master Unit Kerja.',
            'Dapat generate konsep/final PDF SIP Kendaraan, menyetujui/menolak, dan mengupload SIP final yang sudah TTE BSrE.',
        ],
        'Sekretaris Jenderal': [
            'Dapat mereview dan menyetujui SIP Rumah Negara sesuai alur persetujuan Sekjen.',
        ],
    }

    hak_akses = []
    seen = set()
    for role in role_names:
        for item in akses_map.get(role, []):
            if item not in seen:
                hak_akses.append(item)
                seen.add(item)
    if not role_names:
        role_names = ['Belum ada role']
        hak_akses = ['Belum ada hak akses khusus. Hubungi Admin System untuk pengaturan role.']
    return role_names, hak_akses


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Edit profil pribadi user dari menu kanan atas."""
    model = get_user_model()
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('profile_edit')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        role_names, hak_akses = _hak_akses_for_user(self.request.user)
        ctx['profile_role_names'] = role_names
        ctx['profile_hak_akses'] = hak_akses
        ctx['profile_unit_kerja'] = getattr(getattr(self.request.user, 'profile', None), 'unit_kerja', None)
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Profil berhasil diperbarui.')
        return super().form_valid(form)


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('profile_edit')

    def form_valid(self, form):
        messages.success(self.request, 'Kata sandi berhasil diubah.')
        return super().form_valid(form)


# =============================================================
# Export tabel administrasi user/role/log (PDF, Excel, CSV)
# =============================================================
def _require_admin_system(user):
    if not (user.is_superuser or user.groups.filter(name='Admin System').exists()):
        raise PermissionDenied('Hanya Admin System yang dapat melakukan export data ini.')


def _role_names(user):
    names = list(user.groups.values_list('name', flat=True))
    if user.is_superuser:
        names.insert(0, 'Superuser')
    return ', '.join(names) or 'Tanpa role'


def _user_columns():
    return [
        ('No', '__no__'), ('Username', 'username'), ('Nama Lengkap', lambda o: o.get_full_name()),
        ('Email', 'email'), ('Unit Kerja', 'profile__unit_kerja__nama_unit'),
        ('Role', _role_names), ('Aktif', lambda o: 'Aktif' if o.is_active else 'Nonaktif'),
        ('Superuser', lambda o: 'Ya' if o.is_superuser else 'Tidak'), ('Terakhir Login', 'last_login'), ('Tanggal Bergabung', 'date_joined'),
    ]


def _login_history_columns():
    return [
        ('No', '__no__'), ('Waktu Login', 'login_at'), ('Username', 'user__username'),
        ('Nama', lambda o: o.user.get_full_name() if o.user else ''), ('Email', 'user__email'),
        ('Unit Kerja', 'user__profile__unit_kerja__nama_unit'), ('Role', lambda o: _role_names(o.user) if o.user else ''),
        ('IP Address', 'ip_address'), ('User Agent', 'user_agent'),
    ]


def _visit_counter_columns():
    return [
        ('No', '__no__'), ('Username', 'user__username'), ('Nama', lambda o: o.user.get_full_name() if o.user else ''),
        ('Email', 'user__email'), ('Unit Kerja', 'user__profile__unit_kerja__nama_unit'),
        ('Role', lambda o: _role_names(o.user) if o.user else ''), ('Total Kunjungan', 'total_kunjungan'),
        ('Kunjungan Terakhir', 'last_visit_at'), ('Halaman Terakhir', 'last_path'), ('IP Terakhir', 'last_ip_address'),
    ]


def _role_columns():
    return [('No', '__no__'), ('Nama Role', 'name'), ('Jumlah User', lambda o: o.user_set.count())]


@login_required
def export_users(request, fmt):
    _require_admin_system(request.user)
    qs = get_user_model().objects.select_related('profile__unit_kerja').prefetch_related('groups')
    qs = apply_search_filter(qs, request, UserListView.search_fields).distinct()
    return export_queryset(request, qs, fmt, 'manajemen_user', 'Manajemen User', _user_columns(), order_by=['username'])


@login_required
def export_login_history(request, fmt):
    _require_admin_system(request.user)
    qs = LoginHistory.objects.select_related('user', 'user__profile__unit_kerja').prefetch_related('user__groups')
    qs = apply_search_filter(qs, request, LoginHistoryListView.search_fields)
    return export_queryset(request, qs, fmt, 'riwayat_login_user', 'Riwayat Login User', _login_history_columns(), order_by=['-login_at'])


@login_required
def export_visit_counter(request, fmt):
    _require_admin_system(request.user)
    qs = UserVisitCounter.objects.select_related('user', 'user__profile__unit_kerja').prefetch_related('user__groups')
    qs = apply_search_filter(qs, request, UserVisitCounterListView.search_fields)
    return export_queryset(request, qs, fmt, 'counter_kunjungan_user', 'Counter Kunjungan User', _visit_counter_columns(), order_by=['-total_kunjungan', 'user__username'])


@login_required
def export_roles(request, fmt):
    _require_admin_system(request.user)
    qs = Group.objects.all()
    qs = apply_search_filter(qs, request, RoleListView.search_fields)
    return export_queryset(request, qs, fmt, 'manajemen_role', 'Manajemen Role', _role_columns(), order_by=['name'], landscape_mode=False)
