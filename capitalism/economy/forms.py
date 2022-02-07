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

class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.description}"

#! Form for the user to create a new simulation
#! TODO rename this as SimulationCreateForm or something like that
class SimulationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") # store value of request 
        logger.info(f"User {self.request.user} wants to create a new Simulation") 
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset=Project.objects.all()
 
        #* If we wanted to select from a model with a user in it, here is what we would do:
        #*  self.fields['project'].queryset=Simulation_Parameter.objects.filter(user=self.request.user)
        #* This will become relevant when we allow users to create their own projects

    project= MyModelChoiceField(queryset=Simulation_Parameter.objects.all(), initial=0)
#! TODO URGENT - disallow duplicate names

    class Meta:
        model = Simulation_Parameter
        fields=['name','periods_per_year',]
