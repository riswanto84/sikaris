from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group

from master.models import UnitKerja
from .models import UserProfile


class CaptchaLoginForm(AuthenticationForm):
    """Login form dengan captcha angka sederhana.

    Pertanyaan captcha dibuat oleh LoginView dan disimpan di session.
    Field ini mencegah bot/brute-force sederhana tanpa memakai OTP email.
    """
    captcha = forms.CharField(
        label='Captcha',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'Masukkan hasil perhitungan',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'autofocus': True})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

    def clean_captcha(self):
        value = (self.cleaned_data.get('captcha') or '').strip()
        expected = None
        if self.request:
            expected = self.request.session.get('login_captcha_answer')
        if expected is None or value != str(expected):
            raise forms.ValidationError('Captcha tidak sesuai. Silakan coba lagi.')
        return value


class UserCreateForm(UserCreationForm):
    """Form tambah user aplikasi SIKARIS dari halaman internal, bukan Django Admin."""
    email = forms.EmailField(label='Email', required=False)
    first_name = forms.CharField(label='Nama Depan', required=False, max_length=150)
    last_name = forms.CharField(label='Nama Belakang', required=False, max_length=150)
    groups = forms.ModelMultipleChoiceField(
        label='Role / Group',
        queryset=Group.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Pilih role user. Contoh: Admin System, Biro Umum, Pengelola BMN, Pemeliharaan Kendaraan.',
    )
    unit_kerja = forms.ModelChoiceField(
        label='Unit Kerja / Satker',
        queryset=UnitKerja.objects.all().order_by('nama_unit'),
        required=False,
        help_text='Untuk user unit kerja, pilih unit kerja agar akses kendaraan dan rumah dinas dibatasi hanya pada unit tersebut. Kosongkan hanya untuk Admin System/Biro Umum/superuser.',
    )
    is_active = forms.BooleanField(label='Aktif', required=False, initial=True)
    is_staff = forms.BooleanField(
        label='Staff status', required=False,
        help_text='Tidak perlu dicentang untuk user aplikasi biasa. Centang hanya bila user perlu akses Django admin.'
    )
    is_superuser = forms.BooleanField(
        label='Superuser', required=False,
        help_text='Gunakan sangat terbatas. Superuser memiliki akses penuh.'
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'groups', 'unit_kerja', 'is_active', 'is_staff', 'is_superuser',
            'password1', 'password2',
        )
        labels = {
            'username': 'Username',
        }
        help_texts = {
            'username': 'Bisa diisi NIP/email pegawai, tetapi pembatasan akses utama sekarang memakai field Unit Kerja/Satker di bawah.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            self.save_m2m()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'unit_kerja': self.cleaned_data.get('unit_kerja')},
            )
        return user


class UserUpdateForm(forms.ModelForm):
    """Form edit user. Password bersifat opsional."""
    password1 = forms.CharField(
        label='Password Baru', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        help_text='Kosongkan jika tidak ingin mengubah password.'
    )
    password2 = forms.CharField(
        label='Konfirmasi Password Baru', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    groups = forms.ModelMultipleChoiceField(
        label='Role / Group',
        queryset=Group.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    unit_kerja = forms.ModelChoiceField(
        label='Unit Kerja / Satker',
        queryset=UnitKerja.objects.all().order_by('nama_unit'),
        required=False,
        help_text='Untuk user unit kerja, pilih unit kerja agar akses kendaraan dan rumah dinas dibatasi hanya pada unit tersebut. Kosongkan hanya untuk Admin System/Biro Umum/superuser.',
    )

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'groups', 'unit_kerja', 'is_active', 'is_staff', 'is_superuser',
            'password1', 'password2',
        )
        labels = {
            'username': 'Username',
            'email': 'Email',
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'unit_kerja': 'Unit Kerja / Satker',
            'is_active': 'Aktif',
            'is_staff': 'Staff status',
            'is_superuser': 'Superuser',
        }
        help_texts = {
            'username': 'Bisa diisi NIP/email pegawai, tetapi pembatasan akses utama sekarang memakai field Unit Kerja/Satker di bawah.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].initial = self.instance.groups.all()
        profile = getattr(self.instance, 'profile', None)
        if profile:
            self.fields['unit_kerja'].initial = profile.unit_kerja
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get('password1')
        password2 = cleaned.get('password2')
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError('Password baru dan konfirmasi password tidak sama.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
            self.save_m2m()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'unit_kerja': self.cleaned_data.get('unit_kerja')},
            )
        return user


class RoleForm(forms.ModelForm):
    """Form tambah/edit role berbasis Django Group."""
    class Meta:
        model = Group
        fields = ['name']
        labels = {'name': 'Nama Role'}
        help_texts = {'name': 'Contoh: Biro Umum, Pengelola BMN, Pemeliharaan Kendaraan.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama role'})
