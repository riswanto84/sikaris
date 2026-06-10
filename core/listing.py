from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView


class SearchListMixin(LoginRequiredMixin, ListView):
    """
    Mixin daftar data dengan pencarian server-side dan pagination.

    Cara pakai di ListView:
        search_fields = [
            ('nomor_sip', 'Nomor SIP'),
            ('pegawai__nama', 'Nama Pegawai'),
        ]
        select_related = ['pegawai']

    Parameter GET:
        q            : kata kunci
        search_field : field tertentu, atau kosong/ALL untuk semua field
    """
    paginate_by = 15
    search_fields = []
    select_related = []
    prefetch_related = []

    def get_queryset(self):
        qs = super().get_queryset()

        if self.select_related:
            qs = qs.select_related(*self.select_related)

        if self.prefetch_related:
            qs = qs.prefetch_related(*self.prefetch_related)

        q = (self.request.GET.get('q') or '').strip()
        selected_field = (self.request.GET.get('search_field') or 'ALL').strip()

        if q and self.search_fields:
            available_fields = [field for field, _label in self.search_fields]
            fields_to_search = available_fields

            if selected_field != 'ALL' and selected_field in available_fields:
                fields_to_search = [selected_field]

            query = Q()
            for field in fields_to_search:
                query |= Q(**{f'{field}__icontains': q})

            qs = qs.filter(query)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        querydict = self.request.GET.copy()
        querydict.pop('page', None)

        ctx['q'] = self.request.GET.get('q', '')
        ctx['search_field'] = self.request.GET.get('search_field', 'ALL')
        ctx['search_fields'] = self.search_fields
        ctx['pagination_querystring'] = querydict.urlencode()
        ctx['paginate_by'] = self.paginate_by
        return ctx
