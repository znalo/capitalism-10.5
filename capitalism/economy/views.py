from .forms import SimulationCreateForm, SimulationSelectForm, SimulationDeleteForm
from .actions.control import step_execute
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.shortcuts import render
from economy.actions.initialize import initialize_projects
from economy.actions.initialize import initialize
from .models.states import Project, TimeStamp, User, Simulation
from economy.models.report import Trace
from .models.commodity import Commodity
from .models.owners import Industry, SocialClass, StockOwner
from .models.stocks import IndustryStock, SocialStock, Stock
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView,UpdateView, DeleteView, CreateView
from .global_constants import *
from .forms import SignUpForm
from django.contrib.auth import authenticate,login
from django.http.response import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages

def get_economy_view_context(request):#TODO change name - this function now not only creates the context but also displays it, so the naming is wrong
    current_simulation=request.user.current_simulation
    current_time_stamp=current_simulation.current_time_stamp
    industry_stocks = IndustryStock.objects.filter(time_stamp=current_time_stamp)
    industries=Industry.objects.filter(time_stamp=current_time_stamp)
    productive_stocks=industry_stocks.filter(usage_type=PRODUCTION).order_by("commodity__display_order")
    #!all industries have the same choice of productive stocks, even if usage is zero, hence get the headers from the first industry
    industry_headers=productive_stocks.filter(industry=industries.first()).order_by("commodity__display_order") 
    social_classes=SocialClass.objects.filter(time_stamp=current_time_stamp)
    social_stocks=SocialStock.objects.filter(time_stamp=current_time_stamp)
    consumption_stocks=social_stocks.filter(usage_type=CONSUMPTION)
    #!all social classes have the same choice of consumption stocks, even if usage is zero, hence get the headers from the first social class
    consumption_headers=consumption_stocks.filter(social_class=social_classes.first())
    commodities=Commodity.objects.filter(time_stamp=current_time_stamp)

    context={}
    context["simulation"]=current_simulation
    context["productive_stocks"]=productive_stocks
    context["industries"]=industries
    context["industry_headers"]=industry_headers
    context["social_classes"]=social_classes
    context["social_stocks"]=social_stocks
    context["consumption_stocks"]=consumption_stocks
    context["consumption_headers"]=consumption_headers
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
    def get_context_data(self, **kwargs):
        simulation=self.request.user.current_simulation
        context = super().get_context_data(**kwargs)
        qs=TimeStamp.objects.filter(simulation=simulation)
        context['timestamp_list']=qs
        return context
 
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
        current_time_stamp=self.request.user.current_simulation.current_time_stamp        
        context = super().get_context_data(**kwargs)
        qs=Industry.objects.filter(time_stamp=current_time_stamp)
        context['industry_list']=qs
        return context    

class CommodityView(ListView):
    model=Commodity
    template_name='commodity_list.html'
    def get_context_data(self, **kwargs):
        current_time_stamp=self.request.user.current_simulation.current_time_stamp
        context = super().get_context_data(**kwargs)
        qs=Commodity.objects.filter(time_stamp=current_time_stamp).order_by('display_order')
        context['commodity_list']=qs
        return context    

class SocialClassView(ListView):
    template_name='socialclass_list.html'
    model=SocialClass
    def get_context_data(self, **kwargs):
        current_time_stamp=self.request.user.current_simulation.current_time_stamp
        context = super().get_context_data(**kwargs)
        qs=SocialClass.objects.filter(time_stamp=current_time_stamp)
        context['social_class_list']=qs
        return context

class AllOwnersView(ListView):
    model=StockOwner
    template_name='stockowner_list.html'    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_list=StockOwner.objects.order_by("time_stamp.simulation.project_number","time_stamp.time_stamp")
        context['stock_list']= stock_list
        return context


class SocialStockView(ListView):
    model=SocialStock
    template_name='socialstock_list.html'
    def get_context_data(self, **kwargs):
        current_time_stamp=self.request.user.current_simulation.current_time_stamp
        context = super().get_context_data(**kwargs)
        stock_list=SocialStock.objects.filter(time_stamp=current_time_stamp)
        context['stock_list']= stock_list
        return context    

class IndustryStockView(ListView):
    model=IndustryStock
    template_name='industrystock_list.html'
    def get_context_data(self, **kwargs):
        current_time_stamp=self.request.user.current_simulation.current_time_stamp
        context = super().get_context_data(**kwargs)
        stock_list=IndustryStock.objects.filter(time_stamp=current_time_stamp)
        context['stock_list']= stock_list
        return context
        
class AllStocksView(ListView):
    model=Stock
    template_name='stock_list.html'

class TraceView(ListView):
    model=Trace
    template_name='trace_list.html'    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs=Trace.objects.filter(simulation=self.request.user.current_simulation).order_by('real_time')
        context['trace_list']=qs
        return context    

class SimulationView(ListView):
    model=Simulation
    template_name='simulation_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        simulation_list=Simulation.objects.filter(user=self.request.user)
        
        context['simulation_list']= simulation_list

        return context    

#! Executes a single step and then renders the economy
def step_execute_and_display(request,act):
    try:
        step_execute(request=request,act=act)
    except Exception as error:
        logger.error(f"could not execute the action {act} because {error}")
        messages.error(request=request,message=f"could not carry out the step {act} because {error}")
    return get_economy_view_context(request=request)

def landingPage(request):
    user=request.user
    logger.info(f"User {user} has landed on the home page")
    return render(request, 'landing.html')

def status_update(request):
    user=request.user
    logger.info(f"User {user} requested a status update")
    return render(request, 'status.html')

def about_capitalism(request):
    user=request.user
    logger.info(f"User {user} requested the about page")
    return render(request, 'about-capitalism.html')

#! to display messages to people that just logged in
def newlyLanded(request):
    user=request.user
    logger.info(f"User {user} has landed on the new landing page")
    messages.info(request,"Hi, welcome to capitalism")
    messages.info(request, "To view the current state of the project, visit the Status Update Page")
    return render(request, 'landing.html')


#! See the [CSEStack](https://www.csestack.org/django-sign-up-registration-form/) solution
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  #! TODO Not sure if this is needed but seems to be recommended
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            #! Initialise the user's database, creating a set of standard simulations for this user
            initialize(request)         
            return HttpResponseRedirect(reverse("economy"))
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def initialize_and_redisplay(request):
    initialize(request)
    return HttpResponseRedirect(reverse("economy"))    

def disclaimers(request):
    return render(request, 'disclaimers.html')

# TODO the action should ensure that this doesn't corrupt the existing users' simulations (see comments for 'initialize_projects')
def rebuild_project_table(request):
    initialize_projects(request)
    return HttpResponseRedirect(reverse("landing-page"))    

class AdminDashboard(ListView):
    model=User
    template_name='admin-dashboard.html'    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs=User.objects.all()
        context={}
        context['users']=qs
        return context    

def userDashboard(request):
    template = loader.get_template('user-dashboard.html')
    context={}
    context["simulation_list"]=Simulation.objects.filter(user=request.user)
    return HttpResponse(template.render(context, request))    

class UserDetail(DeleteView):
    template_name='user_form.html'    
    model=User
    fields=["username"]
    success_url='admin-dashboard'

class SimulationCreateView(LoginRequiredMixin, CreateView):
    form_class=SimulationCreateForm
    queryset=Simulation.objects.all()
    template_name='simulation_create.html'
    success_url=reverse_lazy('user-dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        logger.info(f"Valid new simulation form submitted by user {self.request.user}")
        simulation_name=form.cleaned_data['name']
        user_project_choice=form.cleaned_data['project']
        logger.info(f"Trying to create a simulation called {simulation_name}")
        chosen_project_number=user_project_choice.number
        logger.info(f"Project number is {chosen_project_number}")
        simulation=form.save(commit=False)
        simulation.user=self.request.user
        simulation.project_number=chosen_project_number
        simulation.save()
        result=simulation.startup()
        if result!="success":
            messages.error(self.request,f"Could not create this simulation because {result}")
        return super(SimulationCreateView, self).form_valid(form)
 
    def form_invalid(self, form):
        logger.info(f"Invalid new simulation form submitted by user {self.request.user}")
        logger.info(f"The non-field errors were {form.non_field_errors}")
        return self.render_to_response( 
            self.get_context_data(form=form))

def simulationSelectView(request,pk):
    user=request.user
    simulation_choice=Simulation.objects.get(user=user, pk=pk)
    time_stamp=simulation_choice.current_time_stamp
    logger.info(f"User {user} is switching to {simulation_choice} with time stamp {time_stamp}")
    user.current_simulation=simulation_choice
    user.save()
    return HttpResponseRedirect(reverse("user-dashboard"))      

class SimulationDeleteView(LoginRequiredMixin, DeleteView):
    model=Simulation
    template_name='simulation_confirm_delete.html'
    success_url=reverse_lazy("user-dashboard")

def simulationRestartView(request,pk):
    user=request.user
    simulation=user.current_simulation
    #! Find the first time stamp in the simulation. Its period will be 0
    first_time_stamp=TimeStamp.objects.get(user=user,simulation=simulation,period=0)
    logger.info(f"User {request.user} is restarting simulation {request.user.current_simulation}")
    logger.info(f"The time stamp is {first_time_stamp}")
    try:
        Commodity.objects.filter(simulation=simulation).exclude(time_stamp=first_time_stamp).delete()
        StockOwner.objects.filter(simulation=simulation).exclude(time_stamp=first_time_stamp).delete()
        Stock.objects.filter(simulation=simulation).exclude(time_stamp=first_time_stamp).delete()
        Trace.objects.filter(simulation=simulation).exclude(time_stamp_id=first_time_stamp.time_stamp).delete()
        TimeStamp.objects.filter(simulation=simulation).exclude(time_stamp=first_time_stamp.time_stamp).delete()
        simulation.current_time_stamp=first_time_stamp
        simulation.save()
    except Exception as error:
        logger.info(f"Failed to restart a simulation because {error}")
        messages.info(request, f"Failed to restart a simulation because {error}")
    return HttpResponseRedirect(reverse("user-dashboard"))      
