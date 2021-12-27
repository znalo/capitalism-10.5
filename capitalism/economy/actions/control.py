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

    # mc=ControlSuperState(name=M_C, first_substate_name=DEMAND, next_superstate_name=C_P)
    # mc.save()
    # demand=ControlSubState(name=DEMAND,super_state_name=M_C, next_substate_name=SUPPLY)
    # demand.save()
    # supply=ControlSubState(name=SUPPLY,super_state_name=M_C, next_substate_name=ALLOCATE)
    # supply.save()
    # allocate=ControlSubState(name=ALLOCATE,super_state_name=M_C, next_substate_name=TRADE)
    # allocate.save()
    # trade=ControlSubState(name=TRADE,super_state_name=M_C,next_substate_name=PRODUCE)
    # trade.save()
    # cp=ControlSuperState(name=C_P,first_substate_name=PRODUCE)
    # cp.save()
    # produce=ControlSubState(name=PRODUCE,super_state_name=C_P, next_substate_name=PRICES)
    # produce.save()
    # prices=ControlSubState(name=PRICES,super_state_name=C_P, next_substate_name=REPRODUCE)
    # prices.save()
    # reproduce=ControlSubState(name=REPRODUCE,super_state_name=C_P, next_substate_name=REVENUE)
    # reproduce.save()
    # cm=ControlSuperState(name=C_M, first_substate_name=REVENUE)
    # cm.save()
    # revenue=ControlSubState(name=REVENUE,super_state_name=C_M,next_substate_name=ACCUMULATE)
    # revenue.save()
    # accumulate=ControlSubState(name=ACCUMULATE,super_state_name=C_M, next_substate_name=DEMAND)
    # accumulate.save()



    Log.enter(1, f"Reading projects from {file_name}")
    df = pd.read_csv(file_name)
    # Project.objects.all().delete()
    for row in df.itertuples(index=False, name='Pandas'):
        project = Project(number=row.project_id, description=row.description)
        project.save()
    # TODO project.owner (currently defaults messily to superuser)

    # TimeStamp.objects.all().delete()
    file_name = os.path.join(settings.BASE_DIR, "static\\timestamps.csv")
    Log.enter(1, f"Reading time stamps from {file_name}")
    df = pd.read_csv(file_name)

    for row in df.itertuples(index=False, name='Pandas'):
        time_stamp = TimeStamp(
            project_FK=Project.objects.get(number=row.project_FK),
            period=row.period,
            # super_state=row.super_state,
            comparator_time_stamp_ID=row.comparator_time_stamp_ID,
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
    # TODO can the below be done more pythonically
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

#! get the current time_stamp object


def get_current_time_stamp():
    # ! there's always only one record in this queryset
    current_state = State.objects.get(name="Initial")
    current_time_stamp = current_state.time_stamp_FK
    this_project = current_time_stamp.project_FK
    time_stamp = TimeStamp.objects.filter(
        project_FK=this_project).order_by('time_stamp').last()
    return time_stamp


def create_stamp():
    Log.enter(0, "MOVING ONE TIME STAMP FORWARD")
    # ! there's always only one record in this queryset
    current_state = State.objects.get(name="Initial")
    current_time_stamp = current_state.time_stamp_FK
    this_project = current_time_stamp.project_FK
    old_time_stamp = TimeStamp.objects.filter(
        project_FK=this_project).order_by('time_stamp').last()
#! create a new timestamp object by saving with pk=None. Forces Django to create a new database object
    new_time_stamp = old_time_stamp
    new_time_stamp.pk = None
    new_time_stamp.time_stamp += 1
    new_time_stamp.description = "NEXT"
    new_time_stamp.save()
#! reset the current state
    current_state.time_stamp_FK = new_time_stamp
    current_state.save()
    Log.enter(
        1, f"Stepping from Old Time Stamp {old_time_stamp} to New Time Stamp {new_time_stamp}; state is now {current_state}")
    return new_time_stamp


#! create a complete clone of each object and set it to point to the new time stamp
#! when this is done, pass through the newly-created children linking them to their new parents
#! cloning method is to set pk=0 and save. See https://django.fun/docs/django-orm-cookbook/en/2.0/copy/
def clone(old_time_stamp, new_time_stamp):
    commodities = Commodity.objects.filter(time_stamp_FK=old_time_stamp)
    for commodity in commodities:
        commodity.pk = None
        commodity.time_stamp_FK = new_time_stamp
        commodity.save()
        Log.enter(
            1, f"Created a new Commodity record {commodity} with time stamp {commodity.time_stamp_FK.time_stamp}")

    industries = Industry.objects.filter(time_stamp_FK=old_time_stamp)
    for industry in industries:
        industry.pk = None
        industry.time_stamp_FK = new_time_stamp
        industry.save()
        Log.enter(
            1, f"Created a new Industry record {industry} with time stamp {industry.time_stamp_FK.time_stamp}")

    social_classes = SocialClass.objects.filter(time_stamp_FK=old_time_stamp)
    for social_class in social_classes:
        social_class.pk = None
        social_class.time_stamp_FK = new_time_stamp
        social_class.save()
        Log.enter(
            1, f"Created a new Social Class record {social_class} with time stamp {social_class.time_stamp_FK.time_stamp}")

    social_stocks = SocialStock.objects.filter(time_stamp_FK=old_time_stamp)
    for social_stock in social_stocks:
        social_stock.pk = None
        social_stock.time_stamp_FK = new_time_stamp
        social_stock.save()
        Log.enter(
            1, f"Created a new Social Stock record {social_stock} with time stamp {social_stock.time_stamp_FK}")

    industry_stocks = IndustryStock.objects.filter(
        time_stamp_FK=old_time_stamp)
    for industry_stock in industry_stocks:
        industry_stock.pk = None
        industry_stock.time_stamp_FK = new_time_stamp
        industry_stock.save()
        Log.enter(
            1, f"Created a new Industry Stock record {industry_stock} with time stamp {industry_stock.time_stamp_FK}")
    return


def connect_stamp(new_time_stamp):
    #! connect industries to their related commodities
    Log.enter(0, "Connecting records")
    industries = Industry.objects.filter(time_stamp_FK=new_time_stamp)
    for industry in industries:
        commodity_name = industry.commodity_FK.name
        Log.enter(
            1, f"Connecting Industry {industry.name} to its output commodity {commodity_name}")
#! find the commodity with the same name but the new time stamp
        candidates = Commodity.objects.filter(
            name=commodity_name, time_stamp_FK=new_time_stamp)
        if candidates.count() > 1:
            Log.enter(0, f"+++DUPLICATE COMMODITIES {candidates}+++")
        else:
            industry.commodity_FK = candidates.get()
        industry.save()
#! connect industry stocks to their commodities and owners
    industry_stocks = IndustryStock.objects.filter(
        time_stamp_FK=new_time_stamp)
    for industry_stock in industry_stocks:
        commodity_name = industry_stock.commodity_FK.name
        Log.enter(
            1, f"Connecting Industry Stock {industry_stock} to commodity {commodity_name}")
#! find the commodity that has the same name but the new time stamp
        new_commodity = Commodity.objects.get(
            name=commodity_name, time_stamp_FK=new_time_stamp)
        industry_stock.commodity_FK = new_commodity
#! find the owner industry
        industry_name = industry_stock.industry_FK.name
        new_industry = Industry.objects.get(
            name=industry_name, time_stamp_FK=new_time_stamp)
        Log.enter(
            1, f"Connecting Industry Stock {industry_stock} to its industry {industry_name}")
        industry_stock.industry_FK = new_industry
        industry_stock.stock_owner_FK= new_industry
        industry_stock.save()
        new_industry.save()
#! connect social stocks to their commodities and owners
    social_stocks = SocialStock.objects.filter(time_stamp_FK=new_time_stamp)
    for social_stock in social_stocks:
        commodity_name = social_stock.commodity_FK.name
        Log.enter(
            1, f"Connecting Social Stock {social_stock} to commodity {commodity_name}")
#! find the commodity that has the same name but the new time stamp
        new_commodity = Commodity.objects.get(
            name=commodity_name, time_stamp_FK=new_time_stamp)
        social_stock.commodity_FK = new_commodity
#! find the owner social class
        social_class_name = social_stock.social_class_FK.name
        new_social_class = SocialClass.objects.get(
            name=social_class_name, time_stamp_FK=new_time_stamp)
        Log.enter(
            1, f"Connecting Social Stock {social_stock} to its social class {social_class_name}")
        social_stock.social_class_FK = new_social_class
        social_stock.stock_owner_FK= new_social_class
        social_stock.save()
        new_social_class.save()

#! Create a new time stamp and new copies of every object, referencing the new time stamp
#! Then connect the object FKs
#! For development purposes, these two operations can be separated using the variable dev

def move_one_stamp_without_display():
    old_time_stamp = get_current_time_stamp()
    new_time_stamp = create_stamp()
    Log.enter(
        0, f"Creating new records: {old_time_stamp} new stamp is: {new_time_stamp}")
    clone(old_time_stamp, new_time_stamp)
    connect_stamp(new_time_stamp)


def move_one_stamp(request):
    old_time_stamp = get_current_time_stamp()
    new_time_stamp = create_stamp()
    Log.enter(
        0, f"Creating new records: {old_time_stamp} new stamp is: {new_time_stamp}")
    clone(old_time_stamp, new_time_stamp)
    connect_stamp(new_time_stamp)
    template = loader.get_template('landing.html')
    context = get_economy_view_context({})
    return HttpResponse(template.render(context, request))

#! Perform the entire set of exchange actions
def c_m_c(request):
    move_one_stamp_without_display()
    
