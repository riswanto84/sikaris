from decimal import Decimal
from django.urls import reverse
from urllib.parse import urlencode


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


def normalize_coordinate_for_maps(value):
    if value in [None, '']:
        return None
    try:
        coord = Decimal(str(value).strip().replace(',', '.'))
        return format(coord, 'f')
    except Exception:
        text = str(value).strip().replace(',', '.')
        try:
            Decimal(text)
            return text
        except Exception:
            return None


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

        # Preview dokumen SIP PDF di halaman detail SIP Kendaraan/Rumah Negara.
        # Berlaku otomatis untuk object yang memiliki field dokumen_sip.
        dokumen_sip = getattr(self.object, 'dokumen_sip', None)
        dokumen_sip_url = None
        dokumen_sip_is_pdf = False
        if dokumen_sip:
            try:
                dokumen_sip_url = dokumen_sip.url
                dokumen_sip_is_pdf = str(dokumen_sip.name).lower().endswith('.pdf')
            except Exception:
                dokumen_sip_url = None
                dokumen_sip_is_pdf = False

        # Preview dokumen kendaraan PDF pada halaman Detail Kendaraan.
        kendaraan_document_previews = []
        for field_name, label in [
            ('dokumen_stnk', 'Preview Dokumen STNK'),
            ('dokumen_bpkb', 'Preview Dokumen BPKB'),
        ]:
            file_obj = getattr(self.object, field_name, None)
            if file_obj:
                try:
                    file_url = file_obj.url
                    is_pdf = str(file_obj.name).lower().endswith('.pdf')
                    kendaraan_document_previews.append({
                        'label': label,
                        'url': file_url,
                        'is_pdf': is_pdf,
                    })
                except Exception:
                    pass

        # Preview Google Maps di halaman detail Rumah Negara/Tanah Negara
        # selama object memiliki latitude dan longitude.
        latitude = getattr(self.object, 'latitude', None)
        longitude = getattr(self.object, 'longitude', None)
        google_maps_embed_url = None
        google_maps_open_url = None
        if latitude not in [None, ''] and longitude not in [None, '']:
            # Koordinat harus memakai titik sebagai desimal untuk URL Google Maps.
            # Jika memakai format lokal Indonesia, misalnya -6,23914800, Google Maps
            # akan salah membaca koma sebagai pemisah koordinat dan peta bisa bergeser ke lokasi global.
            lat = normalize_coordinate_for_maps(latitude)
            lng = normalize_coordinate_for_maps(longitude)
            if lat and lng:
                query = f'{lat},{lng}'
                google_maps_embed_url = 'https://maps.google.com/maps?' + urlencode({
                    'hl': 'id',
                    'll': query,
                    'q': query,
                    'z': 18,
                    't': 'm',
                    'output': 'embed',
                })
                google_maps_open_url = 'https://www.google.com/maps/search/?' + urlencode({
                    'api': 1,
                    'query': query,
                })

        ctx.update({
            'detail_title': self.detail_title,
            'detail_rows': self.get_detail_rows(),
            'back_url': self.get_named_url(self.back_url_name),
            'edit_url': self.get_named_url(self.edit_url_name),
            'delete_url': self.get_named_url(self.delete_url_name),
            'dokumen_sip_url': dokumen_sip_url,
            'dokumen_sip_is_pdf': dokumen_sip_is_pdf,
            'kendaraan_document_previews': kendaraan_document_previews,
            'google_maps_embed_url': google_maps_embed_url,
            'google_maps_open_url': google_maps_open_url,
        })
        return ctx
