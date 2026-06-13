import random

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from core.listing import SearchListMixin
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

    protected_roles = {'Admin System', 'Biro Umum', 'Pengelola BMN', 'Pemeliharaan Kendaraan'}

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.name in self.protected_roles:
            messages.error(request, 'Role bawaan sistem tidak boleh dihapus.')
            return redirect('role_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Role berhasil dihapus.')
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Edit profil pribadi user dari menu kanan atas."""
    model = get_user_model()
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('profile_edit')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profil berhasil diperbarui.')
        return super().form_valid(form)


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('profile_edit')

    def form_valid(self, form):
        messages.success(self.request, 'Kata sandi berhasil diubah.')
        return super().form_valid(form)
