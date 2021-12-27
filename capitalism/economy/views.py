from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import CommoditiesSerializer
from .models.states import TimeStamp, Log
from .models.commodity import Commodity
from .models.owners import Industry, SocialClass, StockOwner
from .models.stocks import IndustryStock, SocialStock, Stock
from .helpers import get_economy_view_context
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView


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
        qs=Industry.time_stamped_queryset()
        context['time_stamped_industry_list']=qs
        return context    

class CommodityView(ListView):
    model=Commodity
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs=Commodity.time_stamped_queryset()
        context['time_stamped_commodity_list']=qs
        return context    

class SocialClassView(ListView):
    model=SocialClass
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs=SocialClass.time_stamped_queryset()
        context['time_stamped_social_class_list']=qs
        return context

class AllOwnersView(ListView):
    model=StockOwner

class SocialStockView(ListView):
    model=SocialStock

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_list=SocialStock.time_stamped_queryset()
        context['stock_list']= stock_list
        return context    

class IndustryStockView(ListView):
    model=IndustryStock
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_list=IndustryStock.time_stamped_queryset()
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

# The viewsets below provide access to the API


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