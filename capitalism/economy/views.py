from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import CommoditiesSerializer
from .models.states import TimeStamp, Log
from .models.commodity import Commodity
from .models.owners import Industry, SocialClass, StockOwner
from .models.stocks import IndustryStock, SocialStock, Stock
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView
from .models.states import State
from capitalism.global_constants import *

def get_economy_view_context(request):#TODO change name - this function now not only creates the context but also displays is, so the naming is wrong
        current_time_stamp=State.get_current_time_stamp()
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
        template = loader.get_template('economy/economy.html')
        return HttpResponse(template.render(context, request))


def sandbox(request):
    table_query = Commodity.objects.all()
  
    template = loader.get_template('economy/sandbox.html')
    context = {
        'table_query': table_query,
    }
    return HttpResponse(template.render(context, request))

class TimeStampView(ListView):
    model=TimeStamp
 
class EconomyView(ListView):
    model=IndustryStock
    template_name='economy/economy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_economy_view_context(context)
        return context

class IndustryView(ListView):
    model=Industry
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # qs=Industry.time_stamped_queryset() #! use this in deployment
        qs=Industry.objects.all()
        context['time_stamped_industry_list']=qs
        return context    

class CommodityView(ListView):
    model=Commodity
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # qs=Commodity.time_stamped_queryset() #! use this in deployment
        qs=Commodity.objects.all()
        context['time_stamped_commodity_list']=qs
        return context    

class SocialClassView(ListView):
    model=SocialClass
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # qs=SocialClass.time_stamped_queryset() #! use this in deployment
        qs=SocialClass.objects.all()
        context['time_stamped_social_class_list']=qs
        return context

class AllOwnersView(ListView):
    model=StockOwner

class SocialStockView(ListView):
    model=SocialStock

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # stock_list=SocialStock.time_stamped_queryset()#! use this in deployment
        stock_list=SocialStock.objects.all()
        context['stock_list']= stock_list
        return context    

class IndustryStockView(ListView):
    model=IndustryStock
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # stock_list=IndustryStock.time_stamped_queryset()#! use this in deployment
        stock_list=IndustryStock.objects.all()
        context['stock_list']= stock_list
        return context
        
class AllStocksView(ListView):
    model=Stock
    
class LogView(ListView):
    model=Log

def log_collapsible(request):
    log_iterator=Log.objects.all().order_by('id')
    template = loader.get_template('economy/log_collapsible.html')
    context = {
        'log_iterator': log_iterator,
    }
    return HttpResponse(template.render(context, request))    

def landingPage(request):
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

class CommodityViewSet(viewsets.ModelViewSet):
    queryset = Commodity.objects.all()
    serializer_class = CommoditiesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'commodities': reverse('commodity-list', request=request, format=format),
    })