from django import template

register = template.Library()


@register.filter
def price(val: int, currency: str):
    if currency == "JPY":
        return "¥ {:,}".format(int(val / 100))
    elif currency == "USD":
        return "${:,}".format(val / 100)
    elif currency == "EUR":
        return "{:,}€".format(val / 100)
    else:
        raise ValueError("unknown currency")
