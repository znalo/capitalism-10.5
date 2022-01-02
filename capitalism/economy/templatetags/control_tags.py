from django.contrib.auth.models import User
from django import template
from ..models.states import State, Log
from capitalism.global_constants import *

register = template.Library()

@register.inclusion_tag('partials/control_states.html')
def control_states():
      context={}
      try:
            current_substate=State.get_current_time_stamp().description
            current_superstate=SUBSTATES[current_substate].superstate_name
      except: #! if anything goes wrong just start at the beginning...
            print("Corrupt initial state encountered {current_substate}; set to start at the beginning of a circuit")
            current_substate=DEMAND
            current_superstate=M_C
      context['active_superstate']=current_superstate
      context['superstates']=SUPERSTATES
      return context

@register.inclusion_tag('partials/current_substate.html')
def current_substate():
      try:
            substate=State.get_current_time_stamp().description
      except:
            substate="corrupted"
      context={}
      context['substate']=substate
      return context
