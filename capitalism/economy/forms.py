from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from economy.models.states import Simulation_Parameter, Project
from economy.models.states import User
from django.forms import ModelChoiceField
from .global_constants import *

# from django.contrib.auth import get_user_model
# User=get_user_model()

class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
        )

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email' )

#! Struggled with this one to pass in the user name. 
#! Not needed yet, but wanted to know how when the time comes
#* See http://django.co.zw/en/tutorials/django-forms-overriding-the-queryset-on-a-select-field-to-exclude-options-already-used/
#* See https://sayari3.com/articles/16-how-to-pass-user-object-to-django-form/

class ProjectChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.description}"

#! Form for the user to create a new simulation
#! TODO rename this as SimulationCreateForm or something like that
class SimulationCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") # store value of request 
        logger.info(f"User {self.request.user} wants to create a new Simulation") 
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset=Project.objects.all()

    #! TODO URGENT - disallow duplicate names
    project= ProjectChoiceField(queryset=Simulation_Parameter.objects.all(), initial=0)

    class Meta:
        model = Simulation_Parameter
        fields=['name','periods_per_year',]

class SimulationChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f"Project {obj.project_number}.{obj.name}"

class SimulationSelectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(SimulationSelectForm, self).__init__(*args, **kwargs)
        logger.info(f"User {request.user} wants to create a new Simulation") 
        self.fields['simulations']=SimulationChoiceField(queryset=Simulation_Parameter.objects.filter(user=request.user))

    class Meta:
        model = Simulation_Parameter
        exclude=('name',
        'project_number',
        'periods_per_year',
        'population_growth_rate',
        'investment_ratio', 
        'labour_supply_response',
        'price_response_type',
        'melt_response_type',
        'currency_symbol',
        'quantity_symbol',
        'user',)    

        