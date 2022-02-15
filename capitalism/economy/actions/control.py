from django.http.response import HttpResponseRedirect
from economy.models.states import TimeStamp
from economy.models.report import Trace
from ..global_constants import *
from django.urls import reverse
from django.contrib import messages
from .steps import ACTION_LIST

def step_execute(request,act):
    #! The various states of the simulation are comprised of stages and steps. The user decides either to execute a single step, or all steps in a stage
    #! We may thus arrive at this point by one of three routes:
        # * because we're only processing stages (user not interested in the detail), and this is one step in a complete stage
        # *  or:
        # * because user has stepped part way through a stage and now wants to skip to the next stage,
        # *  or:
        # * because the user has opted to execute a single step, in which case we'll be called by 'step_execute'
    #! Any failure is handled by views.step_execute_and_display

    user=request.user
    simulation=user.current_simulation
    current_time_stamp=simulation.current_time_stamp

    try:
        action=ACTION_LIST[act]
    except Exception as error:
        raise Exception("The simulation asked for an action that we don't know about. It was called {act}")
    Trace.enter(simulation, 0,f"Executing action {act}")
    logger.info(f"Preparing to execute step {act} in simulation {simulation} with time stamp {current_time_stamp} (id={current_time_stamp.id})")
    simulation.one_step()#! creates new timestamp, ready for the action
    action(simulation=simulation) #! perform the action
    next_step=STEPS[act].next_step
    current_time_stamp.step=next_step
    logger.info(f"The next planned action will be {current_time_stamp.step}")

    #! If we just implemented "demand" then we are at the start of a new period.
    if act==DEMAND:
        current_time_stamp.period+=1        
        logger.info(f"Moving forward one period to {current_time_stamp.period}")
    current_time_stamp.save()
    logger.info(f"Saved a time stamp whose id is {current_time_stamp.id}, with comparator {current_time_stamp.comparator_time_stamp_FK.id}")

def stage_execute(request,act):
    #! Executes an entire stage or, if the user is partway through a stage, executes the remaining steps of that stage
    #! TODO we should probably create an additional time stamp to record the entry into a new stage.
    #* This will improve the comparator functionality; the additional stamp will always show differences with the previous stage
    #* whilst its predecessor step will always show differences with the previous step

    user=request.user
    simulation=user.current_simulation
    current_time_stamp=simulation.current_time_stamp
    while user.current_stage==act:
        logger.info(f"PROCESSING STAGE {act}, PERFORMING STEP {user.current_step}")
        step_execute(request=request,act=user.current_step)
    where_we_are_in_the_mall=user.current_simulation.current_time_stamp
    #! We have executed all the steps of this stage. Now record the fact that the stage has changed
    where_we_are_in_the_mall.stage=user.current_stage
    where_we_are_in_the_mall.save()

    #! TODO set the stage comparator. This ought to work as follows:
      #* If we are executing several steps, the comparator time stamp is at the place we started.
      #* If we haven't executed any steps, this will be the previous stage
      #* If we are midway through a stage, this will be the point in the previous stage that we've reached so far.
    # user.set_current_comparator(remember_where_we_parked)

    return HttpResponseRedirect(reverse("economy"))

def select_comparator(request, period,stage,step):
    logger.info(f"User wants to select new comparator '{period}-{stage}-{step}'")
    try:
        current_time_stamp=request.user.current_simulation.current_time_stamp
        simulation=request.user.simulation
        comparator=TimeStamp.objects.get(simulation_FK=simulation, period=period, stage=stage,step=step,user=request.user)
        current_time_stamp.comparator_time_stamp_FK=comparator
        current_time_stamp.save()
        simulation.comparator_time_stamp=comparator
        simulation.save()
    except Exception as error:
        logger.error(f"Comparator could not be found {period}-{stage}-{step} because {error}")
        messages.error (request, f"Comparator could not be found")

    return HttpResponseRedirect(reverse("economy"))

