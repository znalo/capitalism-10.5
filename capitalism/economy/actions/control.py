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

def step_execute(request,act):
    step_execute_without_display(act)
    return get_economy_view_context(request)

def step_execute_without_display(act):
    action=ACTION_LIST[act]
    State.one_step()#! creates new timestamp, ready for the action
    action()#! perform the action in the new timestamp
    current_time_stamp=State.current_stamp()
    next_step_name=STEPS[act].next_step_name
    current_time_stamp.step_name=next_step_name
    current_time_stamp.step=next_step_name 
    #! If the action that we just implemented was "demand" then we are at the start of a new period.
    if act==DEMAND:
        current_time_stamp.period+=1        
    current_time_stamp.save()
    Log.enter(1,f"Initiate action {act} in {current_time_stamp.step_name} whose stage is {current_time_stamp.stage}")

def stage_execute(request,act):
    remember_where_we_parked=State.current_stamp()
    #! If we are at the start of a stage, execute all the steps within that stage
    #! If we are partway through a stage, this same loop will excecute only the remaining steps in that stage
    #! TODO we should probably create an additional time stamp to record the entry into a new stage.
     #* This will improve the comparator functionality; the additional stamp will always show differences with the previous stage
     #* whilst its predecessor step will always show differences with the previous step
    while State.stage()==act:
        Log.enter(0,f"PROCESSING STAGE {act}, PERFORMING STEP {State.step()}")
        step_execute_without_display(State.step())
    where_we_are_in_the_mall=State.current_stamp()
    #! We have executed all the steps of this stage
    #! Now we have to record the change in stage
    where_we_are_in_the_mall.stage=State.stage()
    where_we_are_in_the_mall.save()

    #! set the comparator. At present (see TODO above) this will work as follows:
     #* If we are executing several steps, the comparator time stamp is at the place we started.
     #* If we haven't executed any steps, this will be the previous stage
     #* If we are midway through a stage, this will be the point in the previous stage that we've reached so far.
    State.set_current_comparator(remember_where_we_parked)
    return HttpResponseRedirect(reverse("economy"))

def select_project(request,id):
    Log.enter(0,f"Switching to project {id}")
    try:
        new_project=Project.objects.get(number=id)
        print (f"found the project and it is {new_project.description}")
        new_time_stamp=TimeStamp.objects.filter(project_FK=new_project).last()
        print (f"found the time stamp and it is {new_time_stamp.step}")
        State.set_project(new_time_stamp)
    except:
        raise Exception ("Cannot find this project - this is a data error. Cannot continue")
    return HttpResponseRedirect(reverse("economy"))

def comparator_select(request,period,stage,step):
    #!TODO implement this. It should set the comparator to the selected state
    Log.enter(1,f"User selected new comparator '{period}-{stage}-{step}'")
    try:
        current_stamp=State.current_stamp()
        comparator=TimeStamp.objects.filter(project_FK=current_stamp.project_FK, period=period, stage=stage,step=step).get()
        current_stamp.comparator_time_stamp_FK=comparator
        current_stamp.save()
    except:
        raise Exception ("This comparator could not be found. This is a programme error. Cannot continue, sorry")

    return HttpResponseRedirect(reverse("economy"))
