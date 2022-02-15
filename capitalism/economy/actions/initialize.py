from economy.models.states import Project, TimeStamp, Simulation
from economy.models.report import Trace
from economy.models.commodity import Commodity
from economy.models.owners import Industry, SocialClass, StockOwner
from economy.models.stocks import IndustryStock, SocialStock, Stock
from economy.actions.exchange import set_initial_capital, set_total_value_and_price
from django.contrib.staticfiles.storage import staticfiles_storage
import pandas as pd
from economy.global_constants import *
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls import reverse


#! The project table is a static table that should only be changed by the admin user
#! The admin user is responsible for ensuring that simulations are not 'orphaned' thereby.
#! If this should happen, the simulations will still exist and function, but the user may lose track of which is which
#! TODO make this more foolproof
def initialize_projects(request):
    logged_in_user=request.user
    logger.info(f"Initialise project table {logged_in_user}")
    if not logged_in_user.is_superuser:
        logger.warning(f"User {logged_in_user} wanted to rebuild the project table and was prevented from doing so")
        messages.warning("Sorry, only the administrator can carry out this function")
        return HttpResponseRedirect(reverse("economy"))
    try:
        file_name = staticfiles_storage.path('data/projects.csv')    
        logger.info (f"User {logged_in_user} is initializing the project table from file {file_name}")
        Project.objects.all().delete()
        df = pd.read_csv(file_name)
        for row in df.itertuples(index=False, name='Pandas'):
            project = Project(number=row.project_id, description=row.description)
            logger.info(f"saving project {project}")
            project.save()
    except Exception as error:
        logger.error(f"Could not load projects because of {error}")
        messages.error(request, f"Sorry, could not load the project file because of {error}")
        return HttpResponseRedirect(reverse("economy"))


#! Create a fresh, complete dataset for a single user
#! Wipes out anything they already have so they can start a new simulation
#! TODO restart a single simulation should be a separate activity
#! TODO and this should probably also be an admin action and also automatically performed on signup
def initialize(request):
    logged_in_user=request.user
    logger.info(f"User {logged_in_user} has asked to reinitialize")
    #TODO 'Do you really want to do this?'

#! Check that there is at least one project object
    if Project.objects.all().count() ==0:
        logger.error("There are no projects")
        messages.error(request,"No projects have been loaded. Please contact the administrator")
        return

#! Clear the decks
    Trace.objects.filter(simulation__user=logged_in_user).delete()
    Simulation.objects.filter(user=logged_in_user).delete()
    Commodity.objects.filter(simulation__user=logged_in_user).delete()
    Stock.objects.filter(simulation__user=logged_in_user).delete()
    StockOwner.objects.filter(simulation__user=logged_in_user).delete()
    TimeStamp.objects.filter(simulation__user=logged_in_user).delete()

#! Simulations
#! Also creates time stamps. 
    #! For historical reasons the data file is called 'time stamps'
    #  TODO insist there is only one entry per project in the CSV file
    file_name = staticfiles_storage.path('data/timestamps.csv')    
    logger.info( f"Reading time stamps from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        #! Create a new simulation
        s=Simulation(user=logged_in_user, 
            name=f"{INITIAL}.{row.project_FK}",
            project_number=row.project_FK,
            population_growth_rate=row.population_growth_rate,
            investment_ratio=row.investment_ratio,
            labour_supply_response=row.labour_supply_response,
            price_response_type=row.price_response_type,
            melt_response_type=row.melt_response_type,
            currency_symbol=row.currency_symbol,
            quantity_symbol=row.quantity_symbol,
        )
        s.save()       
        #! Create a new time stamp
        t = TimeStamp(
            simulation=s,
            period=row.period,
            step=row.description,
            stage="M_C", #! projects must start with this stage TODO remove this field from the CSV file
        )
        t.save()
        s.current_time_stamp=t
        s.comparator_time_stamp=t #! comparator for the first stamp is itself
        s.save()
        #! Create an initial Trace object to mark the start of the simulation
        #! We cannot use 'Trace.enter' because the user's current_simulation has not yet been defined
        Trace.enter(s,0,"INITIALISING")

#! Commodities
    file_name = staticfiles_storage.path('data/commodities.csv')    
    logger.info( f"Reading commodities from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        simulation=Simulation.objects.get(project_number=row.project,user=logged_in_user)
        time_stamp=TimeStamp.objects.get(simulation=simulation)
        logger.info(f"Creating commodity {(row.name)} for simulation {simulation} with time stamp {time_stamp} on behalf of user {logged_in_user}")
        commodity = Commodity(
            time_stamp=time_stamp,
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
            tooltip=row.tooltip,
            simulation=simulation,
        )
        commodity.save()
    
#!Industries
    file_name = staticfiles_storage.path('data/industries.csv')    
    logger.info( f"Reading industries from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        simulation=Simulation.objects.get(project_number=row.project,user=logged_in_user)
        time_stamp=TimeStamp.objects.get(simulation=simulation)
        commodity=Commodity.objects.get(time_stamp=time_stamp, name=row.commodity_name, simulation=simulation)
        logger.info(f"Creating Industry {(row.industry_name)} with output {commodity} for simulation {simulation} with time stamp {time_stamp} on behalf of user {logged_in_user} ")
        industry = Industry(
            time_stamp=time_stamp,
            name=row.industry_name,
            commodity=commodity,
            output_scale=row.output,
            output_growth_rate=row.growth_rate,
            current_capital=0,
            stock_owner_type=INDUSTRY,
            initial_capital=0,
            work_in_progress=0,
            simulation=simulation,
        )
        industry.save()

#! Social Classes
    file_name = staticfiles_storage.path('data/social_classes.csv')
    logger.info( f"Reading social classes from {file_name}")
    df = pd.read_csv(file_name)
    for row in df.itertuples(index=False, name='Pandas'):
        simulation=Simulation.objects.get(project_number=row.project,user=logged_in_user)
        time_stamp=TimeStamp.objects.get(simulation=simulation)
        logger.info(f"Creating Social Class {(row.social_class_name)} for simulation {simulation} with time stamp {time_stamp} on behalf of user {logged_in_user}")
        social_class = SocialClass(
            time_stamp=time_stamp,
            name=row.social_class_name,
            commodity=Commodity.objects.get(time_stamp=time_stamp, name="Labour Power", simulation=simulation),
            stock_owner_type=SOCIAL_CLASS,
            population=row.population,
            participation_ratio=row.participation_ratio,
            consumption_ratio=row.consumption_ratio,
            revenue=row.revenue,
            simulation=simulation,
        )
        social_class.save()

#! Stocks
    file_name = staticfiles_storage.path('data/stocks.csv')        
    logger.info( f"Reading stocks from {file_name}")
    df = pd.read_csv(file_name)

    for row in df.itertuples(index=False, name='Pandas'):
        simulation=Simulation.objects.get(project_number=row.project,user=logged_in_user)
        time_stamp=TimeStamp.objects.get(simulation=simulation)
        if row.owner_type == "CLASS":
            social_class=SocialClass.objects.get(time_stamp=time_stamp, name=row.name,simulation=simulation)
            commodity=Commodity.objects.get(time_stamp=time_stamp, name=row.commodity, simulation=simulation)
            logger.info(f"Creating a stock of commodity {(commodity.name)} of usage type {row.stock_type} for class {(social_class.name)} in simulation {simulation} on behalf of user {logged_in_user}")
            social_stock = SocialStock(
                time_stamp=time_stamp,
                social_class=social_class,
                stock_owner=social_class,
                commodity=commodity,
                consumption_requirement=row.consumption_quantity,
                usage_type=row.stock_type,
                owner_type=SOCIAL_CLASS,
                size=row.quantity,
                demand=0,
                supply=0,
                simulation=simulation,
            )
            
            social_stock.save()
        elif row.owner_type == "INDUSTRY":
            industry=Industry.objects.get(time_stamp=time_stamp, name=row.name, simulation=simulation)
            commodity=Commodity.objects.get(time_stamp=time_stamp, name=row.commodity, simulation=simulation)
            logger.info(f"Creating a stock of {(commodity.name)} of usage type {row.stock_type} for industry {(industry.name)}")
            industry_stock = IndustryStock(
                time_stamp=time_stamp,
                industry=industry,
                stock_owner=industry,
                commodity=commodity,
                production_requirement=row.production_quantity,
                usage_type=row.stock_type,
                owner_type=INDUSTRY,
                size=row.quantity,
                demand=0,
                supply=0,
                simulation=simulation,
            )
            industry_stock.save()
        else:
            logger.error(f"Unknown user type {row.owner_type}")

    #! Create initial values, prices and capitals for all simulations iof this user
    for simulation in Simulation.objects.filter(user=logged_in_user):
        set_total_value_and_price(simulation=simulation)
        set_initial_capital(simulation=simulation)

#! set the user up to point to project 1
    simulation=Simulation.objects.get(user=logged_in_user, project_number=1)
    time_stamp=TimeStamp.objects.get(simulation=simulation)
    logged_in_user.current_simulation=simulation
    simulation.current_time_stamp=time_stamp
    simulation.save()
    logged_in_user.save()
