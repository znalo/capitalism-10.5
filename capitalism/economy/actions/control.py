from datetime import time
from ..models.states import (ControlSubState, ControlSuperState, Project, TimeStamp, State, Log)
from ..models.commodity import Commodity
from ..models.owners import Industry, SocialClass
from ..models.stocks import IndustryStock, SocialStock
from ..helpers import get_economy_view_context
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
import os
import pandas as pd
from capitalism.global_constants import *
from django.shortcuts import redirect
from django.urls import reverse

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

    #TODO use reverse() to get the URLs
    mc=ControlSuperState(name=M_C, first_substate_name=DEMAND, next_superstate_name=C_P)
    mc.save()
    demand=ControlSubState(name=DEMAND,super_state_name=M_C, next_substate_name=SUPPLY, URL=reverse("calculate-demand"))
    demand.save()
    supply=ControlSubState(name=SUPPLY,super_state_name=M_C, next_substate_name=ALLOCATE, URL="exchange/supply")
    supply.save()
    allocate=ControlSubState(name=ALLOCATE,super_state_name=M_C, next_substate_name=TRADE, URL="exchange/allocate")
    allocate.save()
    trade=ControlSubState(name=TRADE,super_state_name=M_C,next_substate_name=PRODUCE, URL="exchange/trade")
    trade.save()
    cp=ControlSuperState(name=C_P,first_substate_name=PRODUCE)
    cp.save()
    produce=ControlSubState(name=PRODUCE,super_state_name=C_P, next_substate_name=PRICES, URL="production/produce")
    produce.save()
    prices=ControlSubState(name=PRICES,super_state_name=C_P, next_substate_name=REPRODUCE, URL="production/prices")
    prices.save()
    reproduce=ControlSubState(name=REPRODUCE,super_state_name=C_P, next_substate_name=REVENUE, URL="production/reproduce")
    reproduce.save()
    cm=ControlSuperState(name=C_M, first_substate_name=REVENUE)
    cm.save()
    revenue=ControlSubState(name=REVENUE,super_state_name=C_M,next_substate_name=ACCUMULATE, URL="distribution/revenue")
    revenue.save()
    accumulate=ControlSubState(name=ACCUMULATE,super_state_name=C_M, next_substate_name=DEMAND, URL="distribution/accumulate")
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
        initial_super_state=ControlSuperState.objects.get(name=C_P)
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

#! For development purposes, moving one stamp is available as a separate user action
#TODO remove this for deployment
def move_one_stamp(request):
    URL=State.perform_next_action()
    print("Moving one stamp - just letting you know")
    return redirect(URL)
    # template = loader.get_template('landing.html')
    # context = get_economy_view_context({})
    # return HttpResponse(template.render(context, request))
