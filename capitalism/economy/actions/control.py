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

#! States are divided into stages and steps. User decides either to execute a single step, or all steps in a stage
#! We may thus arrive at this point by one of three routes:
    # * because we're only processing stages (user not interested in the detail), and this is one step in a complete stage
    # *  or:
    # * because user has stepped part way through a stage and now wants to skip to the next stage,
    # *  or:
    # * because the user has opted to execute a single step, in which case we'll be called by 'step_execute'
def step_execute_without_display(request,act):
    #! carry out the action specified by the key 'act', unless the key is meaningless
    try:
        action=ACTION_LIST[act]
    except Exception as error:
        #! We reach this point if the timestamp contains some unexpected action, eg if the timestamp was given default value of UNDEFINED
        #! TODO eventually, we don't want this to happen at all. For now we just trap it,  render it harmless, and study the cause
        logger.error(f"User {request.user} encountered an undefined timestamp action {act}. Nothing was done")
        messages.warning(request,"Undefined action {act}")
        return
    Trace.enter(request.user, 0,f"Executing action {act}")
    logger.info(f"Preparing to execute action {act}")
    user=request.user
    simulation=user.current_simulation
    current_time_stamp=simulation.current_time_stamp
    logger.info(f"Preparing to execute step {act} in simulation {simulation} with time stamp {current_time_stamp} (id={current_time_stamp.id})")
    simulation.one_step()#! creates new timestamp, ready for the action
    action(user=user)#! perform the action in the state belonging to this user
    next_step=STEPS[act].next_step
    current_time_stamp.step=next_step
    logger.info(f"The next planned action will be {current_time_stamp.step}")
    #! If we just implemented "demand" then we are at the start of a new period.
    if act==DEMAND:
        current_time_stamp.period+=1        
        logger.info(f"Moving forward one period to {current_time_stamp.period}")
    current_time_stamp.save()
    logger.info(f"Initiate action {act} in {current_time_stamp.step} whose stage is {current_time_stamp.stage}")
    logger.info(f"The id of the current time stamp is {current_time_stamp.time_stamp} and that of its comparator is {current_time_stamp.comparator_time_stamp_FK.time_stamp}")


def stage_execute(request,act):
    user=request.user
    current_time_stamp=user.current_time_stamp
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
        simulation=request.user.simulation
        comparator=TimeStamp.objects.get(simulation_FK=simulation, period=period, stage=stage,step=step,user=request.user)
        current_time_stamp.comparator_time_stamp_FK=comparator
        current_time_stamp.save()
    except Exception as error:
        logger.error(f"Comparator could not be found {period}-{stage}-{step} because {error}")
        messages.error (request, f"Comparator could not be found")

    return HttpResponseRedirect(reverse("economy"))

