from economy.global_constants import *
from economy.models.report import Trace
from economy.actions.helpers import (
    set_initial_capital,
    set_current_capital,
    evaluate_unit_prices_and_values,
    calculate_commodity_totals,
    evaluate_stocks,
    )
from economy.actions.exchange import (
    calculate_demand,
    calculate_supply,
    allocate_supply,
    calculate_trade,
    )
from economy.actions.produce import(
    calculate_production,
    calculate_reproduction,
    calculate_price_changes_in_distribution,
    )
from economy.actions.distribution import (
    calculate_revenue,
    calculate_investment,    )

"""
Each function in this module executes one step of a simulation.
They are grouped here for clarity. Sometimes, they only invoke one function. However, this organisation of the code makes it easier to vary the steps - so for example 'revalue' and 'production' carry out three distinct actions, which are coded separately
"""

def demand(simulation):
    set_initial_capital(simulation=simulation)
    calculate_demand(simulation=simulation)
    calculate_supply(simulation=simulation)

def allocate(simulation):
    allocate_supply(simulation)

def trade(simulation):
    calculate_trade(simulation)
    calculate_commodity_totals(simulation,'Checksizes', 'Checkprices', 'Checkvalues')    
    set_current_capital(simulation=simulation)    

def production(simulation):
    calculate_production(simulation=simulation)    # ! The immediate results of production
    calculate_commodity_totals(simulation=simulation)    
    set_current_capital(simulation=simulation)     # ! This does not necessarily display profits etc correctly. But makes clearer what revaluation does

def revalue(simulation):
    evaluate_unit_prices_and_values(simulation=simulation)    # ! We have to revalue the stocks, because unit values and prices have changed
    evaluate_stocks(simulation=simulation)                    # ! Now we can calculate capital and profits arising from the 'immediate process of production'
    set_current_capital(simulation=simulation)

def reprice(simulation):
    calculate_price_changes_in_distribution(simulation)
    evaluate_stocks(simulation=simulation)
    set_current_capital(simulation=simulation)

def reproduce(simulation):
    calculate_reproduction(simulation)

def revenue(simulation):
    calculate_revenue(simulation)

def invest(simulation):
    calculate_investment(simulation)
    set_initial_capital(simulation)

ACTION_LIST = {
    'demand': demand,
    'allocate': allocate,
    'trade': trade,
    'produce': production,
    'revalue': revalue,
    'reprice': reprice,
    'reproduce': reproduce,
    'revenue': revenue,
    'invest': invest,
}
