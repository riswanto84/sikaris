from django.utils import timezone

from .models import UserVisitCounter
from .signals import get_client_ip


class UserVisitCounterMiddleware:
    """Menghitung jumlah kunjungan halaman user yang sudah login.

    Counter hanya dihitung untuk request GET halaman aplikasi, bukan static/media/admin.
    """

    EXCLUDED_PREFIXES = (
        '/static/',
        '/media/',
        '/admin/',
        '/favicon',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.record_visit(request, response)
        return response

    def record_visit(self, request, response):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return
        if request.method != 'GET':
            return
        path = request.path or ''
        if any(path.startswith(prefix) for prefix in self.EXCLUDED_PREFIXES):
            return
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return
        if getattr(response, 'status_code', 200) >= 400:
            return

        counter, _ = UserVisitCounter.objects.get_or_create(user=user)
        counter.total_kunjungan = (counter.total_kunjungan or 0) + 1
        counter.last_visit_at = timezone.now()
        counter.last_path = path[:500]
        counter.last_ip_address = get_client_ip(request)
        counter.last_user_agent = request.META.get('HTTP_USER_AGENT', '')
        counter.save(update_fields=[
            'total_kunjungan',
            'last_visit_at',
            'last_path',
            'last_ip_address',
            'last_user_agent',
        ])
