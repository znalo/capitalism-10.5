from django.contrib.auth.models import User
from django import template
from ..models.states import State
from capitalism.global_constants import *

register = template.Library()

@register.inclusion_tag('partials/control_states.html')
def control_states():
      context={}
      current_substate=State.get_current_time_stamp().description
      current_superstate=SUBSTATES[current_substate].superstate_name
      context['active_superstate']=current_superstate
      context['superstates']=SUPERSTATES
      return context

@register.inclusion_tag('partials/current_substate.html')
def current_substate():
      substate=State.get_current_time_stamp().description
      context={}
      context['substate']=substate
      return context
