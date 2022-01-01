from django.http import HttpResponse
from django.template import loader
from ..models.states import State
from ..actions.exchange import set_initial_capital

def revenue():
    #TODO complete this
    print("Revenue")

def accumulate():
    #TODO complete this
    print("Moses and the Prophets")
    set_initial_capital() #! as soon as we are ready for the next circuit, we should reset the initial capital
     
