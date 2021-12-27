from django import template
from datetime import date, timedelta
from capitalism.global_constants import *

register = template.Library()

# @register.filter(name='commodity_name')
# def commodity_name(value):
#     return value.type

@register.filter(name='money_filter')
def money_filter(value):
    stocks=value.filter(usage_type=MONEY)
    if stocks.count()>1:
        return "DUPLICATE STOCK ERROR"
    else:
        stock=stocks.get()
        return stock.size

@register.filter(name='sales_filter')
def sales_filter(value):
    stocks=value.filter(usage_type=SALES)
    if stocks.count()>1:
        return "DUPLICATE STOCK ERROR"
    else:
        stock=stocks.get()
        return stock.size


@register.filter(name='consumption_filter')
def consumption_filter(value):
    stocks=value.filter(usage_type=CONSUMPTION)
    if stocks.count()>1:
        return "DUPLICATE STOCK ERROR"
    else:
        stock=stocks.get()
        return stock.size

@register.filter
def multiply(value, arg):
    return value * arg