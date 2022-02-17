from economy.global_constants import *
from economy.models.report import Trace
from economy.actions.helpers import (
    set_initial_capital,
    set_current_capital,
    evaluate_commodities,
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
    calculate_investment,
    )

#! Each function in this module executes one step of a simulation.
#! They are grouped here for clarity. Sometimes, they only invoke one function. However,
#! This organisation of the code makes it easier to vary the steps
#! - so for example 'revalue' and 'production' carry out three distinct actions, which are coded separately
#! TODO a bit of DRY abstraction for the code lines that are repeated in every case below

def revalue(simulation):
    set_initial_capital(simulation=simulation)
    calculate_demand(simulation=simulation)
    calculate_supply(simulation=simulation)

def allocate(simulation):
    allocate_supply(simulation)

def trade(simulation):
    calculate_trade(simulation)

def production(simulation):
    calculate_production(simulation=simulation)    # ! The immediate results of production
    evaluate_commodities(simulation=simulation)    # ! We have to revalue the stocks, because unit values and prices have changed
    evaluate_stocks(simulation=simulation)         # ! Now we can calculate capital and profits arising from the 'immediate process of production'
    set_current_capital(simulation=simulation)

def values_and_prices(simulation):
    calculate_price_changes_in_distribution(simulation)

def reproduce(simulation):
    calculate_reproduction(simulation)

def revenue(simulation):
    calculate_revenue(simulation)

def invest(simulation):
    calculate_investment(simulation)

ACTION_LIST = {
    'demand': revalue,
    'allocate': allocate,
    'trade': trade,
    'produce': production,
    'prices': values_and_prices,
    'reproduce': reproduce,
    'revenue': revenue,
    'invest': invest,
}
