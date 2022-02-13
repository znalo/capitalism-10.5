from ..global_constants import *
from economy.actions.exchange import set_initial_capital, calculate_demand, calculate_supply, allocate_supply, calculate_trade, set_total_value_and_price
from economy.actions.produce import calculate_production, calculate_reproduction
from economy.actions.distribution import calculate_revenue, calculate_investment
from economy.models.report import Trace

#! Each function in this module executes one step of a simulation.
#! They are grouped here for clarity
#! TODO a bit of DRY abstraction for the code lines that are repeated in every case below 
#! TODO all these should be defined with respect to a simulation, not a user

def revalue(user):
    simulation=user.current_simulation
    Trace.enter(simulation,1,"EVALUATE DEMAND AND SUPPLY")
    logger.info(f"Calculate demand and supply in simulation {simulation} for user {user}")
    set_initial_capital(simulation=simulation)
    calculate_demand(simulation=simulation)
    calculate_supply(simulation=simulation)

def allocate(user):
    simulation=user.current_simulation
    Trace.enter(simulation,1,"ALLOCATE SUPPLY")
    logger.info(f"Allocate supply in simulation {simulation} for user {user}")
    allocate_supply(simulation)

def trade(user):
    simulation=user.current_simulation
    Trace.enter(simulation,1,"TRADE")
    logger.info(f"Trade in simulation {simulation} for user {user}")
    calculate_trade(simulation)

def production(user):
    simulation=user.current_simulation
    Trace.enter(simulation,1,"PRODUCE")  
    logger.info(f"Produce in simulation {simulation} for user {user}")
    calculate_production(simulation=simulation)

def values_and_prices(user):
    simulation=user.current_simulation
    Trace.enter(simulation,1,"PRICES AND VALUES ARISING FROM PRODUCTION")  
    set_total_value_and_price(simulation=simulation)

def reproduce(user):
    simulation=user.current_simulation
    Trace.enter(simulation,1,"SOCIAL REPRODUCTION")  
    calculate_reproduction(simulation)

def revenue(user):
    simulation=user.current_simulation
    Trace.enter(simulation,1,"REVENUES")  
    calculate_revenue(simulation)

def invest(user):
    simulation=user.current_simulation
    Trace.enter(simulation,1,"INVESTMENT")  
    calculate_investment(simulation)

ACTION_LIST={
    'demand':revalue,
    'allocate':allocate,
    'trade':trade,
    'produce':production,
    'prices':values_and_prices,
    'reproduce':reproduce,
    'revenue': revenue,
    'invest':invest,
    }