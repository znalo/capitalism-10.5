from django.contrib.auth.models import User
from django import template
from ..models.states import ControlSuperState, ControlSubState

register = template.Library()

@register.inclusion_tag('partials/control_states.html')
def control_states():
      super_states = ControlSuperState.objects.all()
      sub_states= ControlSubState.objects.all()
      context={}
      context['superstates']=super_states
      context['substates']=sub_states
      return context

