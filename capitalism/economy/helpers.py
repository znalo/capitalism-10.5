from .models.states import State
from .models.commodity import Commodity
from .models.owners import Industry, SocialClass
from .models.stocks import SocialStock, IndustryStock
from django.http import HttpResponse
from django.template import loader
from capitalism.global_constants import *

def get_economy_view_context(context): ## helper function abstract from EconomyView to be used elsewhere also
        current_time_stamp=State.get_current_time_stamp()
        industry_stocks = IndustryStock.objects.filter(time_stamp_FK=current_time_stamp)
        industries=Industry.objects.filter(time_stamp_FK=current_time_stamp)
        productive_stocks=industry_stocks.filter(usage_type=PRODUCTION)
        industry_headers=productive_stocks.filter(industry_FK=industries.first()) #!all industries have same choice of productive stocks, even if usage is zero
        social_classes=SocialClass.objects.filter(time_stamp_FK=current_time_stamp)
        social_stocks=SocialStock.objects.filter(time_stamp_FK=current_time_stamp)
        commodities=Commodity.objects.filter(time_stamp_FK=current_time_stamp)

        context["productive_stocks"]=productive_stocks
        context["industries"]=industries
        context["industry_headers"]=industry_headers
        context["social_classes"]=social_classes
        context["social_stocks"]=social_stocks
        context["commodities"]= commodities

        return context

def render_economy(request):
    template = loader.get_template('economy.html')
    context = get_economy_view_context({})
    return HttpResponse(template.render(context, request))

