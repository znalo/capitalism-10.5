from django import template
from datetime import date, timedelta
from capitalism.global_constants import *
from economy.models.states import ControlSubState, State
from django.utils.safestring import mark_safe

register = template.Library()

# @register.filter(name='commodity_name')
# def commodity_name(value):
#     return value.type

@register.filter(name='money_filter')
def money_filter(value):
    stocks=value.filter(usage_type=MONEY)
    if stocks.count()>1:
        return "DUPLICATE MONEY STOCKS "
    elif stocks.count()<1:
        return "NO MONEY STOCK"
    else:
        stock=stocks.get()
        return stock.size

@register.filter(name='sales_filter')
def sales_filter(value):
    stocks=value.filter(usage_type=SALES)
    if stocks.count()>1:
        return "DUPLICATE SALES STOCKS"
    elif stocks.count()<1:
        return "NO SALES STOCK"
    else:
        stock=stocks.get()
        return stock.size

@register.filter(name='consumption_filter')
def consumption_filter(value):
    stocks=value.filter(usage_type=CONSUMPTION)
    if stocks.count()>1:
        return "DUPLICATE CONSUMPTION STOCKS"
    elif stocks.count()<1:
        return "NO CONSUMPTION STOCK"
    else:
        stock=stocks.get()
        return stock.size

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter(name='current_control_state')
def current_control_state(value):
    sub_state= State.current_control_substate()
    return sub_state

@register.filter
def has_changed(new,old):
    print(f"old was {new} new is {old}")
    if old==new:
        return new
    else:
        return mark_safe("<span style=\"color:red\">"+str(new)+"</span>")
