from ..helpers import get_economy_view_context
from django.http import HttpResponse
from django.template import loader
from ..models.states import State

def revenue():
    #TODO complete this
    print("Revenue")

def accumulate():
    #TODO complete this
    print("Moses and the Prophets")

def all_distribution():
     print ("Distribute all")
     new_substate=State.move_one_substep()
     revenue()
     new_substate=State.move_one_substep()
     accumulate()
     
