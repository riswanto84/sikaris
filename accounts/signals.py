from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from .models import LoginHistory, UserVisitCounter


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@receiver(user_logged_in)
def record_login_history(sender, request, user, **kwargs):
    """Catat setiap login berhasil agar Admin System bisa memantau user yang masuk."""
    if not user or not user.is_authenticated:
        return

    LoginHistory.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        session_key=getattr(request.session, 'session_key', None),
    )

    UserVisitCounter.objects.get_or_create(user=user, defaults={
        'last_visit_at': timezone.now(),
        'last_path': request.path,
        'last_ip_address': get_client_ip(request),
        'last_user_agent': request.META.get('HTTP_USER_AGENT', ''),
    })
