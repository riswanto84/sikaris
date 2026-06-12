from decimal import Decimal
from django.urls import reverse


def format_number_id(value, decimals=2):
    if value is None or value == '':
        return '-'
    try:
        number = Decimal(str(value))
    except Exception:
        return str(value)
    if number == number.to_integral():
        return f'{int(number):,}'.replace(',', '.')
    return f'{number:,.{decimals}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def format_rupiah(value):
    if value is None or value == '':
        return '-'
    try:
        number = Decimal(str(value))
    except Exception:
        return str(value)
    is_negative = number < 0
    number = abs(number)
    if number == number.to_integral():
        formatted = f'{int(number):,}'.replace(',', '.')
    else:
        formatted = f'{number:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"{'-Rp ' if is_negative else 'Rp '}{formatted}"


def display_model_value(obj, field):
    value = getattr(obj, field.name, None)
    if value is None or value == '':
        return '-'

    display_method = getattr(obj, f'get_{field.name}_display', None)
    if callable(display_method):
        try:
            return display_method() or '-'
        except Exception:
            pass

    if getattr(field, 'is_relation', False):
        return str(value) if value else '-'

    if getattr(field, 'get_internal_type', lambda: '')() in ['DecimalField', 'FloatField', 'IntegerField', 'BigIntegerField', 'PositiveIntegerField']:
        lowered = field.name.lower()
        if any(key in lowered for key in ['nilai', 'biaya', 'harga', 'sewa', 'tarif', 'pnbp']):
            return format_rupiah(value)
        return format_number_id(value)

    if getattr(field, 'get_internal_type', lambda: '')() in ['FileField', 'ImageField']:
        try:
            return value.url if value else '-'
        except Exception:
            return str(value) if value else '-'

    return value


class GenericDetailMixin:
    template_name = 'includes/generic_detail.html'
    detail_title = 'Detail Data'
    back_url_name = None
    edit_url_name = None
    delete_url_name = None
    exclude_fields = ['id']

    def get_detail_rows(self):
        rows = []
        obj = self.object
        for field in obj._meta.fields:
            if field.name in self.exclude_fields:
                continue
            internal_type = getattr(field, 'get_internal_type', lambda: '')()
            value = display_model_value(obj, field)
            rows.append({
                'label': getattr(field, 'verbose_name', field.name).title(),
                'name': field.name,
                'value': value,
                'is_file': internal_type in ['FileField', 'ImageField'] and value != '-',
            })
        return rows

    def get_named_url(self, url_name):
        if not url_name:
            return None
        try:
            return reverse(url_name, kwargs={'pk': self.object.pk})
        except Exception:
            try:
                return reverse(url_name)
            except Exception:
                return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'detail_title': self.detail_title,
            'detail_rows': self.get_detail_rows(),
            'back_url': self.get_named_url(self.back_url_name),
            'edit_url': self.get_named_url(self.edit_url_name),
            'delete_url': self.get_named_url(self.delete_url_name),
        })
        return ctx
