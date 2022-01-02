from datetime import time

from django.http.response import HttpResponseRedirect
from ..models.states import (Project, TimeStamp, State, Log)
from ..models.commodity import Commodity
from ..models.owners import Industry, SocialClass
from ..models.stocks import IndustryStock, SocialStock
from ..views import get_economy_view_context
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
import os
import pandas as pd
from capitalism.global_constants import *
from django.shortcuts import redirect
from django.urls import reverse
from .exchange import calculate_demand_and_supply, allocate_supply, set_initial_capital, set_total_value_and_price, trade
from .produce import producers, prices, reproduce
from .distribution import revenue, invest

#!TODO move this list to the constants file
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
    State.move_one_substep()#! creates new timestamp, ready for the action
    action()#! perform the action in the new timestamp
    current_time_stamp=State.get_current_time_stamp()
    next_substate_name=SUBSTATES[act].next_substate_name
    current_time_stamp.substate_name=next_substate_name
    current_time_stamp.description=next_substate_name 
    current_time_stamp.save()
    Log.enter(1,f"Initiate action {act} in {current_time_stamp.substate_name}")

def super_step_execute(request,act):
    while State.superstate()==act:
        substep_execute_without_display(State.substate())
    return HttpResponseRedirect(reverse("economy"))


#! Gets the whole thing going from CSV static files
# TODO EITHER: Loads of error checking
# TODO OR: only allow input via validated forms
def initialize(request):
    #! Basic setup: projects, timestamps and state
    Log.objects.all().delete()
    file_name = os.path.join(settings.BASE_DIR, "static\\data\\projects.csv")
    Log.enter(0, "+++REDO FROM START+++")
    Log.enter(1,"Read in setup files")
    Project.objects.all().delete()
    TimeStamp.objects.all().delete()

    Log.debug_entry(2, f"Reading projects from {file_name}")
    df = pd.read_csv(file_name)
    # Project.objects.all().delete() (moved to start of this method)
    for row in df.itertuples(index=False, name='Pandas'):
        project = Project(number=row.project_id, description=row.description)
        project.save()
    # TODO project.owner (currently defaults messily to superuser)

    # TimeStamp.objects.all().delete() (moved to start of this method)
    file_name = os.path.join(settings.BASE_DIR, "static\\data\\timestamps.csv")
    Log.debug_entry(2, f"Reading time stamps from {file_name}")
    df = pd.read_csv(file_name)

    for row in df.itertuples(index=False, name='Pandas'):
        time_stamp = TimeStamp(
            project_FK=Project.objects.get(number=row.project_FK),
            period=row.period,
            description=row.description,
            melt=row.MELT,
            population_growth_rate=row.population_growth_rate,
            investment_ratio=row.investment_ratio,
            labour_supply_response=row.labour_supply_response,
            price_response_type=row.price_response_type,
            melt_response_type=row.melt_response_type,
            currency_symbol=row.currency_symbol,
            quantity_symbol=row.quantity_symbol
        )
        time_stamp.save()
        time_stamp.comparator_time_stamp_FK=time_stamp #! no belly-button in first stamp
        time_stamp.save()
        
    state = State(name="Initial", time_stamp_FK=TimeStamp.objects.get(
        time_stamp=1, project_FK__number=1))
    state.save()

    #! Basic setup complete, now read the data files
    #! Commodities
    Commodity.objects.all().delete()
    file_name = os.path.join(settings.BASE_DIR, "static\\data\\commodities.csv")
    Log.debug_entry(2, f"Reading commodities from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        Log.debug_entry(2, f"Creating commodity {Log.sim_object(row.name)}")
        commodity = Commodity(
            time_stamp_FK=TimeStamp.objects.get(
            time_stamp=1,
            project_FK__number=row.project),
            name=row.name,
            origin=row.origin_type,
            unit_value=row.unit_value,
            unit_price=row.unit_price,
            usage=row.function_type,
            turnover_time=row.turnover_time,
            demand=0,
            supply=0,
            allocation_ratio=0,
            display_order=row.display_order,
            image_name=row.image_name,
            tooltip=row.tooltip
        )
        # TODO fix owner
        commodity.save()
    
    #!Industries
    Industry.objects.all().delete()
    file_name = os.path.join(settings.BASE_DIR, "static\\data\\industries.csv")
    Log.debug_entry(2, f"Reading industries from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        this_time_stamp = TimeStamp.objects.get(
            time_stamp=1, project_FK__number=row.project)
        Log.debug_entry(3, f"Creating Industry {Log.sim_object(row.industry_name)}")
        industry = Industry(
            time_stamp_FK=this_time_stamp,
            name=row.industry_name,
            commodity_FK=Commodity.objects.get(time_stamp_FK=this_time_stamp, name=row.commodity_name),
            output_scale=row.output,
            output_growth_rate=row.growth_rate,
            current_capital=0,
            stock_owner_type=INDUSTRY,
            initial_capital=0,
            work_in_progress=0
        )
        # TODO fix owner
        industry.save()

    #! Social Classes
    SocialClass.objects.all().delete()
    file_name = os.path.join(settings.BASE_DIR, "static\\data\\social_classes.csv")
    Log.debug_entry(2, f"Reading social classes from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        this_time_stamp = TimeStamp.objects.get(
            time_stamp=1, project_FK__number=row.project)
        Log.debug_entry(3, f"Creating Social Class {Log.sim_object(row.social_class_name)}")
        social_class = SocialClass(
            time_stamp_FK=this_time_stamp,
            name=row.social_class_name,
            commodity_FK=Commodity.objects.get(
                time_stamp_FK=this_time_stamp, name="Labour Power"),
            stock_owner_type=SOCIAL_CLASS,
            population=row.population,
            participation_ratio=row.participation_ratio,
            consumption_ratio=row.consumption_ratio,
            revenue=row.revenue
        )
        # TODO fix owner
        social_class.save()

    #! Stocks
    # ?Can the below be achieved by deleting all Stock objects?
    # ?And if I delete the children, do the parent objects persist?
    # ? See https://stackoverflow.com/questions/9439730/django-how-do-you-delete-child-class-object-without-deleting-parent-class-objec
    # ? Find out by doing it.
    IndustryStock.objects.all().delete()
    SocialStock.objects.all().delete()

    file_name = os.path.join(settings.BASE_DIR, "static\\data\\stocks.csv")
    Log.debug_entry(2, f"Reading stocks from {file_name}")
    df = pd.read_csv(file_name)

    # TODO can the below be done more efficiently?
    for row in df.itertuples(index=False, name='Pandas'):
        this_time_stamp = TimeStamp.objects.get(time_stamp=1, project_FK__number=row.project)
        if row.owner_type == "CLASS":
            social_class=SocialClass.objects.get(time_stamp_FK=this_time_stamp, name=row.name)
            commodity=Commodity.objects.get(time_stamp_FK=this_time_stamp, name=row.commodity)
            social_stock = SocialStock(
                time_stamp_FK=this_time_stamp,
                social_class_FK=social_class,
                stock_owner_FK=social_class,
                commodity_FK=commodity,
                stock_owner_name=social_class.name,
                consumption_requirement=row.consumption_quantity,
                usage_type=row.stock_type,
                owner_type=SOCIAL_CLASS,
                size=row.quantity,
                demand=0,
                supply=0
            )
            # TODO fix owner
            social_stock.save()
            Log.debug_entry(
                3, f"Created a stock of commodity {Log.sim_object(social_stock.commodity_FK.name)} of usage type {row.stock_type} for class {Log.sim_object(social_stock.social_class_FK.name)} ")
        elif row.owner_type == "INDUSTRY":
            industry=Industry.objects.get(time_stamp_FK=this_time_stamp, name=row.name)
            commodity=Commodity.objects.get(time_stamp_FK=this_time_stamp, name=row.commodity)
            industry_stock = IndustryStock(
                time_stamp_FK=this_time_stamp,
                industry_FK=industry,
                stock_owner_FK=industry,
                commodity_FK=commodity,
                stock_owner_name=industry.name,
                production_requirement=row.production_quantity,
                usage_type=row.stock_type,
                owner_type=INDUSTRY,
                size=row.quantity,
                demand=0,
                supply=0
            )
            # TODO fix owner
            industry_stock.save()
            Log.debug_entry(
                3, f"Created a stock of {Log.sim_object(industry_stock.commodity_FK.name)} of usage type {row.stock_type} for industry {Log.sim_object(industry_stock.industry_FK.name)}")
        else:
            Log.enter(0, f"++++UNKNOWN OWNER TYPE++++ {row.owner_type}")
    set_total_value_and_price()
    set_initial_capital()

    #! temporary for development purposes - quick and dirty visual report on what was done. 
    # TODO the logging system should replace this report
    template = loader.get_template('economy/initialize.html')
    context = {}
    context['projects'] = Project.objects.all()
    context['time_stamps'] = TimeStamp.objects.all()
    context['commodities'] = Commodity.objects.all()
    context['industries'] = Industry.objects.all()
    context['social_classes'] = SocialClass.objects.all().order_by(
        'time_stamp_FK__number')
    context['industry_stocks'] = IndustryStock.objects.all()
    context['social_stocks'] = SocialStock.objects.all()
    return HttpResponse(template.render(context, request))

