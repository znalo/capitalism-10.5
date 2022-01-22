from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from .models.states import TimeStamp, Log
from .models.commodity import Commodity
from .models.owners import Industry, SocialClass, StockOwner
from .models.stocks import IndustryStock, SocialStock, Stock
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView
from .models.states import State
from .global_constants import *
from django.urls import reverse


def get_economy_view_context(request):#TODO change name - this function now not only creates the context but also displays is, so the naming is wrong
        current_time_stamp=State.current_stamp()
        industry_stocks = IndustryStock.objects.filter(time_stamp_FK=current_time_stamp)
        industries=Industry.objects.filter(time_stamp_FK=current_time_stamp)
        productive_stocks=industry_stocks.filter(usage_type=PRODUCTION).order_by("commodity_FK__display_order")
        industry_headers=productive_stocks.filter(industry_FK=industries.first()).order_by("commodity_FK__display_order") #!all industries have same choice of productive stocks, even if usage is zero
        social_classes=SocialClass.objects.filter(time_stamp_FK=current_time_stamp)
        social_stocks=SocialStock.objects.filter(time_stamp_FK=current_time_stamp)
        commodities=Commodity.objects.filter(time_stamp_FK=current_time_stamp)

        context={}
        context["productive_stocks"]=productive_stocks
        context["industries"]=industries
        context["industry_headers"]=industry_headers
        context["social_classes"]=social_classes
        context["social_stocks"]=social_stocks
        context["commodities"]= commodities
        template = loader.get_template('economy.html')
        return HttpResponse(template.render(context, request))


def sandbox(request):
    table_query = Commodity.objects.all()
  
    template = loader.get_template('sandbox.html')
    context = {
        'table_query': table_query,
    }
    logger.error("Test!!")
    return HttpResponse(template.render(context, request))

class TimeStampView(ListView):
    model=TimeStamp
    template_name='timestamp_list.html'    
 
class EconomyView(ListView):
    model=IndustryStock
    template_name='economy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_economy_view_context(context)
        return context

#! toggle logging mode between verbose and clean
def switch_log_mode(request):
    if Log.logging_mode=="verbose":
        Log.logging_mode="clean"
    else:
        Log.logging_mode="verbose"
    return HttpResponseRedirect(reverse("economy"))


class IndustryView(ListView):
    model=Industry
    template_name='industry_list.html'    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # qs=Industry.time_stamped_queryset() #! use this in deployment
        qs=Industry.objects.all()
        context['time_stamped_industry_list']=qs
        return context    

class CommodityView(ListView):
    model=Commodity
    template_name='commodity_list.html'    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # qs=Commodity.time_stamped_queryset() #! use this in deployment
        qs=Commodity.objects.all()
        context['time_stamped_commodity_list']=qs
        return context    

class SocialClassView(ListView):
    template_name='socialclass_list.html'
    model=SocialClass
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # qs=SocialClass.time_stamped_queryset() #! use this in deployment
        qs=SocialClass.objects.all()
        context['time_stamped_social_class_list']=qs
        return context

class AllOwnersView(ListView):
    model=StockOwner
    template_name='stockowner_list.html'    

class SocialStockView(ListView):
    model=SocialStock
    template_name='socialstock_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # stock_list=SocialStock.time_stamped_queryset()#! use this in deployment
        stock_list=SocialStock.objects.all()
        context['stock_list']= stock_list
        return context    

class IndustryStockView(ListView):
    model=IndustryStock
    template_name='industrystock_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # stock_list=IndustryStock.time_stamped_queryset()#! use this in deployment
        stock_list=IndustryStock.objects.all()
        context['stock_list']= stock_list
        return context
        
class AllStocksView(ListView):
    model=Stock
    template_name='stock_list.html'    

    
class LogView(ListView):
    model=Log
    template_name='log_list.html'    

def log_collapsible(request):
    log_iterator=Log.objects.all().order_by('id')
    template = loader.get_template('log_collapsible.html')
    context = {
        'log_iterator': log_iterator,
    }
    return HttpResponse(template.render(context, request))    

def landingPage(request):
    print('landing page running a little test')
    try:
        stamp=State.current_stamp()
        print (f"State on arrival at the landing page is {stamp.time_stamp}")
    except Exception as error:
        print(f"Corrupt database; reinitializing to a failsafe initial state")
        print(error)
        State.failsafe_restart()
    return render(request, 'landing.html')

#! The viewsets below provide access to the API
#! This development branch currently not being followed
def apiViews(request):
    return render(request, 'api_views.html')

def commodityTable(request):
    return render(request, 'api-commodities.html')

def projectTable(request):
    return render(request, 'api-projects.html')

def industryTable(request):
    return render(request, 'api-industries.html')

def socialClassTable(request):
    return render(request, 'api-social-classes.html')

def socialStockTable(request):
    return render(request, 'api-social-stocks.html')

def industryStockTable(request):
    return render(request, 'api-industry-stocks.html')

def timeStampTable(request):
    return render(request, 'api-time-stamps.html')

