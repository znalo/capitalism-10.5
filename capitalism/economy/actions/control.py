from django.http.response import HttpResponseRedirect
from economy.models.states import Project, TimeStamp, User
from economy.models.report import Trace
from economy.views import get_economy_view_context
from ..global_constants import *
from django.urls import reverse
from economy.actions.exchange import calculate_demand_and_supply, allocate_supply, trade
from economy.actions.produce import producers, prices, reproduce
from economy.actions.distribution import revenue, invest
from django.contrib import messages

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
    step_execute_without_display(request=request,act=act)
    return get_economy_view_context(request=request)

def step_execute_without_display(request,act):
    try:
        action=ACTION_LIST[act]
    except Exception as error:
        #! We reach this point if the timestamp contains some unexpected action
        #! This can occur if the timestamp was given its default value of UNDEFINED
        #! Or if it was the 'Initial' timestamp that is given to a user when that user is created.
        #! TODO eventually, we don't want this to happen at all. For now we just trap it and render it harmless.
        #! Then we can study the cause
        logger.error(f"User {request.user} encountered an undefined timestamp action {act}. Nothing was done")
        messages.warning("There was a minor programming error. Please inform the developer")
        return
    user=request.user
    current_time_stamp=user.current_time_stamp
    user.one_step()#! creates new timestamp, ready for the action
    action(user=user)#! perform the action in the state belonging to this user
    next_step=STEPS[act].next_step
    current_time_stamp.step=next_step
    #! If the action that we just implemented was "demand" then we are at the start of a new period.
    if act==DEMAND:
        current_time_stamp.period+=1        
    current_time_stamp.save()
    logger.info(f"Initiate action {act} in {current_time_stamp.step} whose stage is {current_time_stamp.stage}")
    logger.info(f"The id of the current time stamp is {current_time_stamp.time_stamp} and that of its comparator is {current_time_stamp.comparator_time_stamp_FK.time_stamp}")


def stage_execute(request,act):
    user=request.user
    current_time_stamp=user.current_time_stamp
    remember_where_we_parked=current_time_stamp
    #! If we are at the start of a stage, execute all the steps within that stage
    #! If we are partway through a stage, this same loop will excecute only the remaining steps in that stage
    #! TODO we should probably create an additional time stamp to record the entry into a new stage.
     #* This will improve the comparator functionality; the additional stamp will always show differences with the previous stage
     #* whilst its predecessor step will always show differences with the previous step
    while user.current_stage==act:
        logger.info(f"PROCESSING STAGE {act}, PERFORMING STEP {user.current_step}")
        step_execute_without_display(request=request,act=user.current_step)
    where_we_are_in_the_mall=user.current_time_stamp
    #! We have executed all the steps of this stage
    #! Now we have to record the change in stage
    where_we_are_in_the_mall.stage=user.current_stage
    where_we_are_in_the_mall.save()

    # #! set the comparator. At present (see TODO above) this will work as follows:
    #  #* If we are executing several steps, the comparator time stamp is at the place we started.
    #  #* If we haven't executed any steps, this will be the previous stage
    #  #* If we are midway through a stage, this will be the point in the previous stage that we've reached so far.
    # user.set_current_comparator(remember_where_we_parked)
    return HttpResponseRedirect(reverse("economy"))

def select_project(request,project_number):
    user=request.user
    Trace.enter(user,0,f"Switching to project {project_number}")
    logger.info(f"User {user} is switching to project {project_number}")
    user.set_project(project_number)
    return HttpResponseRedirect(reverse("economy"))

def comparator_select(request, period,stage,step):
    logger.info(f"User wants to select new comparator '{period}-{stage}-{step}'")
    try:
        current_time_stamp=request.user.current_time_stamp
        current_project_number=request.user.current_project
        comparator=TimeStamp.objects.get(project_number=current_project_number, period=period, stage=stage,step=step,user=request.user)
        current_time_stamp.comparator_time_stamp_FK=comparator
        current_time_stamp.save()
    except Exception as error:
        logger.error(f"Comparator could not be found {period}-{stage}-{step} because {error}")
        messages.error (request, f"Comparator could not be found")

    return HttpResponseRedirect(reverse("economy"))

