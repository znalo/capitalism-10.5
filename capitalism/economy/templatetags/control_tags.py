from django.contrib.auth.models import User
from django import template
from ..models.states import ControlSuperState, ControlSubState

register = template.Library()

@register.inclusion_tag('economy/control_states.html')
def control_states():
      obj = ControlSuperState.objects.values_list('name', flat=True)
      return {'superstates': obj}
