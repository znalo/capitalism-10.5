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
        if old==new:
            return new
        else:
            return mark_safe(f"<span style=\'color:red\'>{new:.0f}</span> (<span style=\'color:green\'>{old:.0f}</span>)")


@register.filter(name='money_filter')
def money_filter(value):
    return stock_compare(MONEY, value)

@register.filter(name='sales_filter')
def sales_filter(value):
    return stock_compare(SALES, value)

@register.filter(name='consumption_filter')
def consumption_filter(value):
    return stock_compare(CONSUMPTION, value)

@register.filter #! TOD redundant I think - this was just a test to see how filters work
def multiply(value, arg):
    return value * arg

@register.filter
def has_changed(new,old):
    if old==new:
        return new
    else:
        return mark_safe(f"<span style=\'color:red\'>{new:.0f}</span> (<span style=\'color:green\'>{old:.0f}</span>)")

@register.filter(is_safe=True)
def mark_as_safe(value):
    return mark_safe(value)