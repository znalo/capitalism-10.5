from ..global_constants import *
from economy.actions.exchange import (
    calculate_demand, 
    calculate_supply, 
    allocate_supply, 
    calculate_trade, 
)
from economy.actions.produce import calculate_production, calculate_reproduction, calculate_price_changes_in_distribution
from economy.actions.distribution import calculate_revenue, calculate_investment
from economy.models.report import Trace
from economy.actions.helpers import set_initial_capital, set_current_capital, evaluate_commodities, evaluate_stocks

#! Each function in this module executes one step of a simulation.
#! They are grouped here for clarity
#! TODO a bit of DRY abstraction for the code lines that are repeated in every case below 
#! TODO all these should be defined with respect to a simulation, not a user

def revalue(simulation):
    Trace.enter(simulation,1,"EVALUATE DEMAND AND SUPPLY")
    logger.info(f"Calculate demand and supply in simulation {simulation} for user {simulation.user}")
    set_initial_capital(simulation=simulation)
    calculate_demand(simulation=simulation)
    calculate_supply(simulation=simulation)

def allocate(simulation):
    Trace.enter(simulation,1,"ALLOCATE SUPPLY")
    logger.info(f"Allocate supply in simulation {simulation} for user {simulation.user}")
    allocate_supply(simulation)

def trade(simulation):
    Trace.enter(simulation,1,"TRADE")
    logger.info(f"Trade in simulation {simulation} for user {simulation.user}")
    calculate_trade(simulation)

def production(simulation):
    Trace.enter(simulation,1,"PRODUCE")  
    logger.info(f"Produce in simulation {simulation} for user {simulation.user}")
    calculate_production(simulation=simulation)
    evaluate_commodities(simulation=simulation) #! The immediate results of production
    evaluate_stocks(simulation=simulation) #! We have to revalue the stocks, because unit values and prices have changed

def values_and_prices(simulation):
    Trace.enter(simulation,1,"PRICES AND VALUES ARISING FROM PRODUCTION")  
    logger.info(f"Calculate prices and values arising from production in simulation {simulation} for user {simulation.user}")
    calculate_price_changes_in_distribution(simulation)
    

def reproduce(simulation):
    Trace.enter(simulation,1,"SOCIAL REPRODUCTION")  
    logger.info(f"Social Reproduction in simulation {simulation} for user {simulation.user}")
    calculate_reproduction(simulation)

def revenue(simulation):
    Trace.enter(simulation,1,"REVENUES")  
    logger.info(f"Calculate revenues in simulation {simulation} for user {simulation.user}")
    calculate_revenue(simulation)

def invest(simulation):
    Trace.enter(simulation,1,"INVESTMENT")  
    logger.info(f"Investment in simulation {simulation} for user {simulation.user}")
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