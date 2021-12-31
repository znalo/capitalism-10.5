from datetime import time
from ..models.states import (ControlSubState, ControlSuperState, Project, TimeStamp, State, Log)
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
from .exchange import calculate_demand,calculate_supply, allocate_supply, trade, all_exchange
from .produce import producers, prices, reproduce, all_production
from .distribution import revenue, accumulate, all_distribution

action_list={
    'Demand':calculate_demand,
    'Supply':calculate_supply,
    'Allocate':allocate_supply,
    'Trade':trade,
    'Produce':producers,
    'Prices':prices,
    'Reproduce':reproduce,
    'Revenue': revenue,
    'Accumulate':accumulate,
    'All_exchange':all_exchange,
    'All_production': all_production,
    'All_distribution': all_distribution
    }

def sub_step_execute(request,act):
    print (f"action {act} requested")
    action=action_list[act]
    print(f"this will execute {action} ")
    new_substate=State.move_one_substep()#! creates new timestamp, ready for the action
    action()#! perform the action in the new timestamp
    return get_economy_view_context(request)

def super_step_execute(request,act):
    print (f"superstate {act} requested")
    action=action_list[act]
    print(f"this will execute {action} ")
    action()

    template = loader.get_template('economy/economy.html')
    context = get_economy_view_context({})
    return HttpResponse(template.render(context, request))    

#! Gets the whole thing going from CSV static files
# TODO EITHER: Loads of error checking
# TODO OR: only allow input via validated forms
def initialize(request):
    #! Basic setup: projects, timestamps and state
    Log.objects.all().delete()
    file_name = os.path.join(settings.BASE_DIR, "static\projects.csv")
    Log.enter(0, "+++REDO FROM START+++")

    ControlSuperState.objects.all().delete()
    ControlSubState.objects.all().delete()
    Project.objects.all().delete()
    TimeStamp.objects.all().delete()

    mc=ControlSuperState(name=M_C, first_substate_name=DEMAND, next_superstate_name=C_P, URL="All_exchange")
    mc.save()
    cp=ControlSuperState(name=C_P,first_substate_name=PRODUCE,next_superstate_name=C_M, URL="All_production")
    cp.save()
    cm=ControlSuperState(name=C_M, first_substate_name=REVENUE, next_superstate_name=M_C, URL="All_distribution")
    cm.save()

    demand=ControlSubState(name=DEMAND,super_state_name=M_C, next_substate_name=SUPPLY, next_super_state_name=M_C, URL="execute/demand")
    demand.save()
    supply=ControlSubState(name=SUPPLY,super_state_name=M_C, next_substate_name=ALLOCATE, next_super_state_name=M_C, URL="execute/supply")
    supply.save()
    allocate=ControlSubState(name=ALLOCATE,super_state_name=M_C, next_substate_name=TRADE, next_super_state_name=M_C, URL="execute/allocate")
    allocate.save()
    trade=ControlSubState(name=TRADE,super_state_name=M_C,next_substate_name=PRODUCE, next_super_state_name=C_P, URL="execute/trade")
    trade.save()
    produce=ControlSubState(name=PRODUCE,super_state_name=C_P, next_substate_name=PRICES, next_super_state_name=C_P, URL="execute/produce")
    produce.save()
    prices=ControlSubState(name=PRICES,super_state_name=C_P, next_substate_name=REPRODUCE, next_super_state_name=C_P, URL="execute/prices")
    prices.save()
    reproduce=ControlSubState(name=REPRODUCE,super_state_name=C_P, next_substate_name=REVENUE, next_super_state_name=C_M, URL="execute/reproduce")
    reproduce.save()
    revenue=ControlSubState(name=REVENUE,super_state_name=C_M,next_substate_name=ACCUMULATE, next_super_state_name=C_M, URL="execute/revenue")
    revenue.save()
    accumulate=ControlSubState(name=ACCUMULATE,super_state_name=C_M, next_substate_name=DEMAND, next_super_state_name=M_C, URL="execute/accumulate")
    accumulate.save()

    Log.enter(1, f"Reading projects from {file_name}")
    df = pd.read_csv(file_name)
    # Project.objects.all().delete() (moved to start of this method)
    for row in df.itertuples(index=False, name='Pandas'):
        project = Project(number=row.project_id, description=row.description)
        project.save()
    # TODO project.owner (currently defaults messily to superuser)

    # TimeStamp.objects.all().delete() (moved to start of this method)
    file_name = os.path.join(settings.BASE_DIR, "static\\timestamps.csv")
    Log.enter(1, f"Reading time stamps from {file_name}")
    df = pd.read_csv(file_name)

    for row in df.itertuples(index=False, name='Pandas'):
        initial_super_state=ControlSuperState.objects.get(name=M_C)
        initial_sub_state=ControlSubState.objects.get(name=DEMAND)
        time_stamp = TimeStamp(
            project_FK=Project.objects.get(number=row.project_FK),
            period=row.period,
            super_state_FK=initial_super_state,
            sub_state_FK=initial_sub_state,
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
    file_name = os.path.join(settings.BASE_DIR, "static\\commodities.csv")
    Log.enter(1, f"Reading commodities from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        Log.enter(2, f"Creating Commodity {row.name}")
        commodity = Commodity(
            time_stamp_FK=TimeStamp.objects.get(
                time_stamp=1, project_FK__number=row.project),
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
    file_name = os.path.join(settings.BASE_DIR, "static\\industries.csv")
    Log.enter(1, f"Reading industries from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        this_time_stamp = TimeStamp.objects.get(
            time_stamp=1, project_FK__number=row.project)
        Log.enter(2, f"Creating Industry {row.industry_name}")
        industry = Industry(
            time_stamp_FK=this_time_stamp,
            name=row.industry_name,
            commodity_FK=Commodity.objects.get(
                time_stamp_FK=this_time_stamp, name=row.commodity_name),
            output_scale=row.output,
            output_growth_rate=row.growth_rate,
            stock_owner_type=INDUSTRY            
        )
        # TODO fix owner
        industry.save()

    #! Social Classes
    SocialClass.objects.all().delete()
    file_name = os.path.join(settings.BASE_DIR, "static\\social_classes.csv")
    Log.enter(1, f"Reading social classes from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        this_time_stamp = TimeStamp.objects.get(
            time_stamp=1, project_FK__number=row.project)
        Log.enter(2, f"Creating Social Class {row.social_class_name}")
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

    file_name = os.path.join(settings.BASE_DIR, "static\\stocks.csv")
    Log.enter(1, f"Reading stocks from {file_name}")
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
            Log.enter(
                2, f"Created {row.stock_type} stock of commodity {social_stock.commodity_FK.name} for class {social_stock.social_class_FK.name}")
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
            Log.enter(
                2, f"Created {row.stock_type} stock of commodity {industry_stock.commodity_FK.name} for industry {industry_stock.industry_FK.name}")
        else:
            Log.enter(0, f"++++UNKNOWN OWNER TYPE++++ {row.owner_type}")

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

