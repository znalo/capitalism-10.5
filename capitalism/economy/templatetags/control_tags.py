from django.contrib.auth.models import User
from django import template
from ..models.states import ControlSuperState, ControlSubState, State

register = template.Library()

@register.inclusion_tag('partials/control_states.html')
def control_states():
      super_states = ControlSuperState.objects.all()
      sub_states= ControlSubState.objects.all()
      current_superstate=State.current_control_superstate()
      context={}
      context['active_superstate']=current_superstate
      context['superstates']=super_states
      context['substates']=sub_states
      return context

@register.inclusion_tag('partials/current_substate.html')
def current_substate():
      substate=State.current_control_substate()
      print(f"PASSING {substate.URL} to navbar")
      context={}
      context['substate']=substate
