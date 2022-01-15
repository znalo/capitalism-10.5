from django.http.response import HttpResponseRedirect
from economy.models.states import (Project, TimeStamp, State, Log)
from economy.views import get_economy_view_context
from capitalism.global_constants import *
from django.urls import reverse
from economy.actions.exchange import calculate_demand_and_supply, allocate_supply, set_initial_capital, set_total_value_and_price, trade
from economy.actions.produce import producers, prices, reproduce
from economy.actions.distribution import revenue, invest

#!TODO move this list to the constants file?
ACTION_LIST={
    'demand':calculate_demand_and_supply,
    'allocate':allocate_supply,
    'trade':trade,
    'produce':producers,
    'prices':prices,
    'reproduce':reproduce,
    'revenue': revenue,
    'invest':invest,
    }

def sub_step_execute(request,act):
    substep_execute_without_display(act)
    return get_economy_view_context(request)

def substep_execute_without_display(act):
    action=ACTION_LIST[act]
    State.substep()#! creates new timestamp, ready for the action
    action()#! perform the action in the new timestamp
    current_time_stamp=State.current_stamp()
    next_substate_name=SUBSTATES[act].next_substate_name
    current_time_stamp.substate_name=next_substate_name
    current_time_stamp.substate=next_substate_name 
    current_time_stamp.save()
    Log.enter(1,f"Initiate action {act} in {current_time_stamp.substate_name} whose superstate is {current_time_stamp.super_state}")

def super_step_execute(request,act):
    remember_where_we_parked=State.current_stamp()
    #! If we are at a superstate, execute all the substates within that superstate
    #! If we are partway through a superstate, this same loop will excecute only the remaining substates in that superstate
    #! TODO we should probably create an additional time stamp to record the entry into a new superstate.
     #* This will improve the comparator functionality; the additional stamp will always show differences with the previous superstate
     #* whilst its predecessor substate will always show differences with the previous substate
    while State.superstate()==act:
        substep_execute_without_display(State.substate())
    where_we_are_in_the_mall=State.current_stamp()
    #! We have executed all the substates of this superstate
    #! Now we have to record the change in superstate
    where_we_are_in_the_mall.super_state=State.superstate()
    where_we_are_in_the_mall.save()

    #! set the comparator. At present (see TODO above) this will work as follows:
     #* If we are executing several substates, the comparator time stamp is at the place we started.
     #* If we haven't executed any substates, this will be the previous superstate
     #* If we are midway through a superstate, this will be the point in the previous superstate that we've reached so far.
    State.set_current_comparator(remember_where_we_parked)
    return HttpResponseRedirect(reverse("economy"))

def select_project(request,id):
    Log.enter(0,f"Switching to project {id}")
    try:
        new_project=Project.objects.get(number=id)
        print (f"found the project and it is {new_project.description}")
        new_time_stamp=TimeStamp.objects.filter(project_FK=new_project).last()
        print (f"found the time stamp and it is {new_time_stamp.substate}")
        State.set_project(new_time_stamp)
    except:
        raise Exception ("Cannot find this project - this is a data error. Cannot continue")
    return HttpResponseRedirect(reverse("economy"))

def comparator_select(request,state,step):
    #!TODO implement this. It should set the comparator to the selected state
    Log.enter(1,f"User selected new comparator '{state}-{step}'")
    return HttpResponseRedirect(reverse("economy"))
