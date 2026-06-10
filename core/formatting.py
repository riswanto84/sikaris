from decimal import Decimal, InvalidOperation


def format_rupiah(value):
    if value is None or value == '':
        return 'Rp 0'

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return value

    is_negative = amount < 0
    amount = abs(amount)

    if amount == amount.to_integral():
        number = f'{int(amount):,}'.replace(',', '.')
    else:
        number = f'{amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    return f'{"-Rp " if is_negative else "Rp "}{number}'
