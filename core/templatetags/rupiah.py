from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()


@register.filter(name='rupiah')
def rupiah(value):
    """
    Format angka menjadi currency Rupiah Indonesia.
    Contoh:
    499900000 -> Rp 499.900.000
    499900000.50 -> Rp 499.900.000,50
    """
    if value is None or value == '':
        return 'Rp 0'

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return value

    is_negative = amount < 0
    amount = abs(amount)

    # Jika tidak ada desimal, tampilkan tanpa ,00
    if amount == amount.to_integral():
        number = f'{int(amount):,}'.replace(',', '.')
    else:
        number = f'{amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    prefix = '-Rp ' if is_negative else 'Rp '
    return f'{prefix}{number}'


@register.filter(name='rupiah_no_symbol')
def rupiah_no_symbol(value):
    """
    Format angka Rupiah tanpa simbol.
    Contoh:
    499900000 -> 499.900.000
    """
    formatted = rupiah(value)
    return formatted.replace('Rp ', '').replace('-Rp ', '-')
