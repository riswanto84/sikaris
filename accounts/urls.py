from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    RoleCreateView,
    RoleDeleteView,
    RoleListView,
    RoleUpdateView,
    SecureLoginView,
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserUpdateView,
    ProfileUpdateView,
    UserPasswordChangeView,
    LoginHistoryListView,
    UserVisitCounterListView,
)


urlpatterns = [
    path('login/', SecureLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/ubah-password/', UserPasswordChangeView.as_view(), name='password_change'),

    path('users/', UserListView.as_view(), name='user_list'),
    path('users/tambah/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/hapus/', UserDeleteView.as_view(), name='user_delete'),

    path('login-history/', LoginHistoryListView.as_view(), name='login_history_list'),
    path('visit-counter/', UserVisitCounterListView.as_view(), name='visit_counter_list'),

    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/tambah/', RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/edit/', RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/hapus/', RoleDeleteView.as_view(), name='role_delete'),
]
