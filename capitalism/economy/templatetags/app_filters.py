from django import template
from ..global_constants import *
from django.utils.safestring import mark_safe

register = template.Library()

def stock_compare(usage_type, value):
    stocks=value.filter(usage_type=usage_type)
    if stocks.count()>1:
        return f"DUPLICATE {usage_type} STOCKS"
    elif stocks.count()<1:
        return F"NO {usage_type} STOCK"
    else:
        current_stock=stocks.get()  
        comparator_stock=current_stock.comparator_stock
        new=current_stock.size
        old=comparator_stock.size
        return has_changed(new,old)


@register.filter(name='money_filter')
def money_filter(value):
    return stock_compare(MONEY, value)

@register.filter(name='sales_filter')
def sales_filter(value):
    return stock_compare(SALES, value)

@register.filter(name='consumption_filter')
def consumption_filter(value):
    return stock_compare(CONSUMPTION, value)

@register.filter # TODO redundant I think - this was just a test to see how filters work
def multiply(value, arg):
    return value * arg

@register.filter
def percent_has_changed(new,old):
    #! I got defeated trying to construct a filter with multiple arguments, so I created two filters
    #! one of which does 2 decimal places and the other does 0. This one does 2
    new_string=f"{new:.2f}"
    old_string=f"{old:.2f}"
    if old==new:
        return mark_safe(new_string)
    else:
        return mark_safe(f"<span style=\'color:red\'>{new_string}</span> (<span style=\'color:green\'>{old_string}</span>)")


@register.filter
def has_changed(new,old):
    #! I got defeated trying to construct a filter with multiple arguments, so I created two filters
    #! one of which does 2 decimal places and the other does 0. This one does 2
    new_string=f"{new:,.0f}"
    old_string=f"{old:,.0f}"
    if old==new:
        return mark_safe(f"<span style=\'color:blue\'>{new_string}</span>")
    else:
        return mark_safe(f"<span style=\'color:red\'>{new_string}</span> (<span style=\'color:green\'>{old_string}</span>)")

@register.filter(is_safe=True)
def mark_as_safe(value):
    return mark_safe(value)

@register.filter
def percentage(value):
    return format(float(value), ".2%")