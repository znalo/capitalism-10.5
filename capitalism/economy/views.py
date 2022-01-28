from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from .models.states import Project, TimeStamp, User
from economy.models.report import Log
from .models.commodity import Commodity
from .models.owners import Industry, SocialClass, StockOwner
from .models.stocks import IndustryStock, SocialStock, Stock
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView
from .global_constants import *
from django.urls import reverse
from .forms import SignUpForm
from django.contrib.auth import authenticate,login

def get_economy_view_context(request):#TODO change name - this function now not only creates the context but also displays it, so the naming is wrong
        current_time_stamp=request.user.current_time_stamp
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

class ProjectView(ListView):
    model=Project
    template_name='project_list.html'

class TimeStampView(ListView):
    model=TimeStamp
    template_name='timestamp_list.html'    
 
class EconomyView(ListView):
    model=IndustryStock
    template_name='economy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #! Necessary?
        context = get_economy_view_context(context)
        return context

class IndustryView(ListView):
    model=Industry
    template_name='industry_list.html'    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs=Industry.objects.filter(time_stamp_FK=self.request.user.current_time_stamp)
        context['industry_list']=qs
        return context    

class CommodityView(ListView):
    model=Commodity
    template_name='commodity_list.html'    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs=Commodity.objects.filter(time_stamp_FK=self.request.user.current_time_stamp)
        context['commodity_list']=qs
        return context    

class SocialClassView(ListView):
    template_name='socialclass_list.html'
    model=SocialClass
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs=SocialClass.objects.filter(time_stamp_FK=self.request.user.current_time_stamp)
        context['social_class_list']=qs
        return context

class AllOwnersView(ListView):
    model=StockOwner
    template_name='stockowner_list.html'    

class SocialStockView(ListView):
    model=SocialStock
    template_name='socialstock_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_list=SocialStock.objects.filter(time_stamp_FK=self.request.user.current_time_stamp)
        context['stock_list']= stock_list
        return context    

class IndustryStockView(ListView):
    model=IndustryStock
    template_name='industrystock_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_list=IndustryStock.objects.filter(time_stamp_FK=self.request.user.current_time_stamp)
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
    try:
        user=User.objects.get(username="afree") #! Little check to see the admin user exists
        logger.info(f"Temporary fix: picking up admin user {user}")
    except Exception as error:
        logger.error(f"Could not find the admin user because of {error}")
    return render(request, 'landing.html')

# class SignupView(generic.CreateView):
#     template_name='registration/signup.html'
#     form_class=CustomUserCreationForm

#     def get_success_url(self):
#         return reverse("login")

#! See the [CSEStack](https://www.csestack.org/django-sign-up-registration-form/) solution
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  
            # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
 
            # login user after signing up
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
 
            # redirect user to home page
            # return redirect('home')
            return HttpResponseRedirect(reverse("economy"))
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})