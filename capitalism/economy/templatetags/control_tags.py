from django.contrib.auth.models import User
from django import template
from economy.models.states import State, Log, Project, TimeStamp
from ..global_constants import *

register = template.Library()

#! supplies list of stages for the dropdown menu
@register.inclusion_tag('partials/stages.html')
def control_states():
      context={}
      try:
            current_step=State.current_stamp().step
            current_stage=STEPS[current_step].stage_name
      except Exception as error: 
      #! if anything goes wrong, report to the user as if the simulation is the at the beginning... (TODO: very temporary)
            print(f"Corrupt initial state encountered due to the cause listed below ; the user menu has been set to start at the beginning of a circuit")
            print(error)
            current_step=DEMAND
            current_stage=M_C
      context['active_stage']=current_stage
      context['stages']=STAGES
      return context

@register.inclusion_tag('partials/current_step.html')
def current_step():
      try:
            step=State.current_stamp().step
      except:
            step="unknown"
      context={}
      context['step']=step
      return context

@register.inclusion_tag('partials/current_logging_mode.html')
def logging_mode():
      logging_mode=Log.logging_mode
      #! The toggle button says what we want to switch to - so it's the opposite of the actual logging state
      toggle_to="clean" if logging_mode=="verbose" else "verbose" 
      context={}
      context['toggle_to']=toggle_to
      return context

@register.inclusion_tag('partials/project_list.html')
def project_list():
      project_list=Project.objects.all()
      context={}
      context['projects']= project_list
      return context

@register.inclusion_tag('partials/step_list.html')
def step_list():
      try:
            current_project=State.current_project()
            state_list=TimeStamp.objects.filter(project_FK=current_project)
      except:
            state_list=TimeStamp.objects.all()
      context={}
      context['states']= state_list
      return context
