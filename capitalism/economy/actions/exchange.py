from django.contrib import messages
from economy.actions.helpers import evaluate_commodities, set_initial_capital,set_current_capital
from economy.models.report import Trace
from economy.models.commodity import Commodity
from economy.models.owners import StockOwner
from economy.models.stocks import Stock, IndustryStock, SocialStock
from ..global_constants import *

def calculate_demand(simulation):
    #! Calculate the unconstrained demand for all stocks
    #! Use this to calculate the total demand for each commodity
    #! In 'allocate' we impose constraints arising from supply and (TODO) money shortages
    current_time_stamp=simulation.current_time_stamp
    periods_per_year=simulation.periods_per_year
    user=simulation.user
    logger.info(f"Calculate demand for simulation {simulation} for {user} with {periods_per_year} periods")
    Trace.enter(simulation,1,"Calculate Demand")
    productive_stocks = IndustryStock.objects.filter(usage_type=PRODUCTION,time_stamp=current_time_stamp)
    social_stocks = SocialStock.objects.filter(time_stamp=current_time_stamp).exclude(usage_type=MONEY).exclude(usage_type=SALES)
    commodities = Commodity.objects.filter(time_stamp=current_time_stamp).exclude(usage=MONEY)

    for commodity in commodities:
        commodity.demand = 0
        commodity.save() #TODO can probably be dispensed with

    for stock in productive_stocks:
        turnover_time = stock.commodity.turnover_time/periods_per_year
        stock.demand = stock.production_requirement*turnover_time
        stock.demand -= stock.size #! We only want to bring the stock size up to what is needed to produce at the current scale
        stock.monetary_demand=stock.demand*commodity.unit_price
        stock.save()
        commodity = stock.commodity
        commodity.demand += stock.demand
        Trace.enter(simulation,2,f"{Trace.sim_object(stock.stock_owner.name)}'s stock of {Trace.sim_object(stock.commodity.name)} is {Trace.sim_quantity(stock.size)}; production requirement is {Trace.sim_quantity(stock.production_requirement)} and turnover time is {Trace.sim_quantity(turnover_time)}. Demand is increased by {Trace.sim_quantity(stock.demand)} to {Trace.sim_quantity(commodity.demand)}")
        commodity.save()

    for stock in social_stocks:
        social_class = stock.social_class
        stock.consumption_requirement = social_class.population*social_class.consumption_ratio/periods_per_year  
        stock.demand = stock.consumption_requirement
        stock.demand -= stock.size #! We only want to bring the stock size up to what is needed to produce at the current scale
        commodity = stock.commodity
        stock.monetary_demand=stock.demand*commodity.unit_price
        stock.save()
        commodity.demand += stock.demand
        Trace.enter(simulation,2,f"{Trace.sim_object(stock.social_class.name)}'s demand for {Trace.sim_object(stock.commodity.name)} is increased by {Trace.sim_quantity(stock.demand)} and is now {Trace.sim_quantity(commodity.demand)}")
        commodity.save()

def calculate_supply(simulation):
    user=simulation.user
    current_time_stamp=simulation.current_time_stamp
    logger.info(f"Calculate supply for simulation {simulation} for user {user}")
    Trace.enter(simulation,1,"Calculate supply")
    #! Initialize every commodity's supply field to zero, prior to recalculating it from sales stocks
    commodities = Commodity.objects.filter(time_stamp=current_time_stamp).exclude(usage=MONEY)
    for commodity in commodities:
        commodity.supply = 0
        commodity.save()
    #! Calculate aggregate individual supply from the sales stocks and assign it to the appropriate commodity's supply field
    stocks = Stock.objects.filter( time_stamp=current_time_stamp,usage_type=SALES)
    for stock in stocks:
        commodity = stock.commodity
        #? at this point supply is the same as the stock size, but may get scaled down if global supply is excessive
        stock.supply = stock.size
        stock.save()
        commodity.supply += stock.supply
        Trace.enter(simulation,2,f" Supply of {Trace.sim_object(commodity.name)} from owner {Trace.sim_object(stock.stock_owner.name)} is {Trace.sim_quantity(stock.size)}. Total supply is now {Trace.sim_quantity(commodity.supply)}")
        commodity.save()

def allocate_supply(simulation):
    current_time_stamp=simulation.current_time_stamp
    logger.info(f"Allocate supply in simulation {simulation} for user {simulation}")
    Trace.enter(simulation,1,"Allocate demand depending on supply")
    commodities = Commodity.objects.filter(time_stamp=current_time_stamp).exclude(usage=MONEY)
    for commodity in commodities:
        Trace.enter(simulation,2,f" Allocating supply for commodity {Trace.sim_object(commodity.name)} whose supply is {Trace.sim_quantity(commodity.supply)} and demand is {Trace.sim_quantity(commodity.demand)}")
        if commodity.supply > 0:
        #! round to avoid silly float errors
            commodity.allocation_ratio = round(commodity.demand/commodity.supply, 4)
            Trace.enter(simulation,3,f" Allocation ratio is {Trace.sim_object(commodity.allocation_ratio)}")
        if commodity.demand>commodity.supply: # demand is greater than supply, reduce it
            commodity.demand=commodity.supply
            Trace.enter(simulation,3,f" Demand was greater than supply and is reduced to commodity.demand")
        commodity.save()

        related_stocks = commodity.stock_set.filter(time_stamp=current_time_stamp)
        for stock in related_stocks:
            if commodity.allocation_ratio>1: # demand is greater than supply, reduce it
                stock.demand=stock.demand/commodity.allocation_ratio
                Trace.enter(simulation,3,f"This stock's demand cannot be satisfied, and is reduced to {Trace.sim_quantity(stock.demand)}")
                stock.save()
            else:
                Trace.enter(simulation,3,"The demand for this commodity is equal to its supply, so this stock's demand is unchanged")

def calculate_trade(simulation):
    current_time_stamp=simulation.current_time_stamp
    #! iterate over all stocks that want to buy a commodity
    buyer_stocks=Stock.objects.filter(time_stamp=current_time_stamp).exclude(usage_type=MONEY).exclude(usage_type=SALES)
    for buyer_stock in buyer_stocks:
        #! mostly, we use these local variables for debugging, but it also helps clarity
        buyer=buyer_stock.stock_owner
        buyer_name=buyer.name
        buyer_commodity=buyer_stock.commodity
        buyer_money_stock=buyer.money_stock
        buyer_verbs=buyer.verbs()
        Trace.enter(simulation,2,f"{Trace.sim_object(buyer_name)} will spend up to ${Trace.sim_quantity(buyer_money_stock.size)} to get {Trace.sim_quantity(buyer_stock.demand)} of {Trace.sim_object(buyer_commodity.name)} for an {Trace.sim_object(buyer_commodity.usage)} stock with origin {Trace.sim_object(buyer_commodity.origin)}. The unit price is ${Trace.sim_quantity(buyer_commodity.unit_price)}")
        
        #! iterate over all potential sellers of this commodity
        potential_sellers=StockOwner.objects.filter(time_stamp=current_time_stamp)

        for seller in potential_sellers:
            seller_name=seller.name
            seller_stock=seller.sales_stock
            seller_commodity=seller_stock.commodity
            seller_money_stock=seller.money_stock
            seller_verbs=seller.verbs()
            if seller_commodity==buyer_commodity:
                Trace.enter(simulation,2,f"SALE:{Trace.sim_object(seller_name)} can sell up to {Trace.sim_quantity(seller_stock.supply)} of {Trace.sim_object(seller_commodity.name)} to {Trace.sim_object(buyer.name)}")
                sale(seller_stock,buyer_stock,seller,buyer, seller_money_stock,buyer_money_stock)
                Trace.enter(simulation,3,f"Buyer status after sale: {Trace.sim_object(buyer.name)} now {buyer_verbs[1]} {Trace.sim_quantity(buyer_stock.size)} of {Trace.sim_object(seller_commodity.name)} and ${Trace.sim_quantity(buyer_money_stock.size)}")
                Trace.enter(simulation,3,f"Seller status after sale: {Trace.sim_object(seller.name)} now {seller_verbs[1]} {Trace.sim_quantity(seller_stock.size)} of {Trace.sim_object(seller_commodity.name)} and ${Trace.sim_quantity(seller_money_stock.size)}")
            else:
                Trace.enter(simulation,4,f"NO SALE: {Trace.sim_object(seller_name)} cannot help")
        Trace.enter(simulation,2,f"BUYER FINAL STATUS: {Trace.sim_object(buyer.name)} now {buyer_verbs[1]} {Trace.sim_quantity(buyer_stock.size)} with value ${Trace.sim_quantity(buyer_stock.value)} and price ${Trace.sim_quantity(buyer_stock.price)}")    
    
    #!Every industry now has the goods with which they will start production.
    #!At the end of this process, we (and the owners) want to know how much profit the industries have made
    #!Therefore, we now establish the total value and price of each commodity and stock
    #!Then, the initial and current capital of each industry
    evaluate_commodities(simulation=simulation)
    set_initial_capital(simulation=simulation)
    set_current_capital(simulation=simulation)

def sale(seller_stock, buyer_stock, seller, buyer, seller_money_stock,buyer_money_stock):
    try:
        simulation=seller.simulation
        transferred_stock=min(buyer_stock.demand,seller_stock.supply)
        logger.info(f"Transferring {transferred_stock} from {seller.name} to {buyer.name}")
        commodity=buyer_stock.commodity
        cost=transferred_stock*commodity.unit_price

        buyer_stock.change_size(transferred_stock)
        seller_stock.change_size(-transferred_stock)
        seller_stock.supply+=transferred_stock
        buyer_stock.demand-=transferred_stock
        Trace.enter(simulation,1,f"Buyer transaction state: {Trace.sim_object(buyer.name)} {buyer.verbs[1]} buying {Trace.sim_quantity(transferred_stock)} of {Trace.sim_object(seller_stock.commodity.name)} from {Trace.sim_object(seller.name)} for ${Trace.sim_quantity(cost)}")
        Trace.enter(simulation,3,f"Seller transaction state: {seller.verbs[2]} ${Trace.sim_quantity(seller_money_stock.size)} and {buyer.verbs[2]} ${Trace.sim_quantity(buyer_money_stock.size)}")
        seller_stock.save()
        buyer_stock.save()
        #!TODO Bizarrely, the code below does not always work if the seller and buyer are the same
        buyer_money_stock.change_size(-cost)
        buyer_money_stock.save()    
        seller_money_stock.change_size(cost)
        seller_money_stock.save()
    except Exception as error:
        logger.error(f"Attempted sale failed because of {error}: details {type(error).__name__} {__file__} {error.__traceback__.tb_lineno} ")
        return
   

