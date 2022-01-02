from django import template
from datetime import date, timedelta
from capitalism.global_constants import *
from economy.models.states import State
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
        comparator_stock=current_stock.comparator_stock()
        new=current_stock.size
        old=comparator_stock.size
        if old==new:
            return new
        else:
            return mark_safe("<span style=\"color:red\">"+str(new)+"</span>")    


@register.filter(name='money_filter')
def money_filter(value):
    return stock_compare(MONEY, value)

@register.filter(name='sales_filter')
def sales_filter(value):
    return stock_compare(SALES, value)

@register.filter(name='consumption_filter')
def consumption_filter(value):
    return stock_compare(CONSUMPTION, value)

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter(name='current_control_sub_state')
def current_control_sub_state(value):
    sub_state= State.get_current_time_stamp().sub_state_name
    return sub_state

@register.filter(name='current_control_super_state')
def current_control_super_state(value):
    super_state= State.current_control_superstate()
    return super_state.URL

@register.filter
def has_changed(new,old):
    if old==new:
        return new
    else:
        return mark_safe("<span style=\"color:red\">"+str(new)+"</span>")

@register.filter(is_safe=True)
def mark_as_safe(value):
    return mark_safe(value)