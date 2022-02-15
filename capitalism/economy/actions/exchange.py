from economy.models.states import User
from economy.models.report import Trace
from economy.models.commodity import Commodity
from economy.models.owners import Industry, SocialClass, StockOwner
from economy.models.stocks import Stock, IndustryStock, SocialStock
from ..global_constants import *
from django.contrib import messages

#! Calculate the unconstrained demand for all stocks
#! Use this to calculate the total demand for each commodity
#! Later (in 'allocate') we impose constraints arising from supply and (TODO) money shortages
def calculate_demand(simulation):
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
        Trace.enter(simulation,2,f"{Trace.sim_object(stock.stock_owner_name)}'s stock of {Trace.sim_object(stock.commodity.name)} is {Trace.sim_quantity(stock.size)}; production requirement is {Trace.sim_quantity(stock.production_requirement)} and turnover time is {Trace.sim_quantity(turnover_time)}. Demand is increased by {Trace.sim_quantity(stock.demand)} to {Trace.sim_quantity(commodity.demand)}")
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
        Trace.enter(simulation,2,f" Supply of {Trace.sim_object(commodity.name)} from the industry {Trace.sim_object(stock.stock_owner_name)} is {Trace.sim_quantity(stock.size)}. Total supply is now {Trace.sim_quantity(commodity.supply)}")
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
        buyer=buyer_stock.stock_owner
        buyer_commodity=buyer_stock.commodity
        Trace.enter(simulation,3,f"{Trace.sim_object(buyer.name)} seeks to purchase {Trace.sim_quantity(buyer_stock.demand)} of {Trace.sim_object(buyer_commodity.name)} for stock of usage type {Trace.sim_object(buyer_commodity.usage)} whose origin is {Trace.sim_object(buyer_commodity.origin)}")
        buyer_money_stock=buyer.money_stock
        Trace.enter(simulation,3,f"The buyer has {Trace.sim_quantity(buyer_money_stock.size)} in money and the unit price is {Trace.sim_quantity(buyer_commodity.unit_price)}. Looking for sellers")
        
        #! iterate over all potential sellers of this commodity
        potential_sellers=StockOwner.objects.filter(time_stamp=current_time_stamp)

        for seller in potential_sellers:
            seller_name=seller.name
            seller_stock=seller.sales_stock
            seller_commodity=seller_stock.commodity
            Trace.enter(simulation,3,f"{Trace.sim_object(seller_name)} can offer {Trace.sim_quantity(seller_stock.supply)} of {Trace.sim_object(seller_commodity.name)} for sale to {Trace.sim_object(buyer.name)} who wants {Trace.sim_object(buyer_commodity.name)}")
            if seller_commodity==buyer_commodity:
                sale(seller_stock,buyer_stock,seller,buyer)
        #!The below is much clearer but does not work. TODO find out why
        # sellers=potential_sellers.filter(commodity=buyer_commodity) 
        #! this returns an empty query, but only for social classes. 
        #! No idea why.
        # for seller in sellers:
        #     seller_name=seller.name
        #     seller_stock=seller.sales_stock()
        #     seller_commodity=seller_stock.commodity
        #     sale(seller_stock,buyer_stock,seller,buyer)

    #!Every industry now has the goods with which they will start production.
    #!At the end of this process, we (and the owners) want to know how much profit the industries have made
    #!Therefore, we now establish:
        #* What is the total value and price of each commodity?
        #* What is the total value and price of each stock?
        #* What is the total value and price of each industry (its capital)?
        #* Note that though the total price of the assets of each owner will be unchanged by trade
        #* the value of these assets will - as a result of unequal exchange
        #* So we make this calculation both before and after production
    set_total_value_and_price(simulation=simulation)
    #! A moot point.
    #! We establish the initial capital at this point, though it was already calculated at the 'demand' stage for technical reasons
    #! This attributes those profits which arise entirely from production (as opposed to transfers in trade) 
    #! to the individual enterprises in which they are generated
    #! TODO this could cause confusion, because we also set current capital in the demand stage 
    #! to avoid division by zero after the project has been initialised for the first time
    set_current_capital(simulation=simulation)

def sale(seller_stock, buyer_stock, seller, buyer):
    simulation=seller.simulation
    transferred_stock=min(buyer_stock.demand,seller_stock.supply)
    commodity=buyer_stock.commodity
    cost=transferred_stock*commodity.unit_price
    seller_stock.size-=transferred_stock
    buyer_stock.size+=transferred_stock
    seller_money_stock=seller.money_stock
    buyer_money_stock=buyer.money_stock
    Trace.enter(simulation,1,f"Sale: {Trace.sim_object(buyer.name)} is buying {Trace.sim_quantity(transferred_stock)} of {Trace.sim_object(seller_stock.commodity.name)} from {Trace.sim_object(seller.name)} at a cost of {Trace.sim_quantity(cost)}")
    Trace.enter(simulation,1,f"The seller has ${Trace.sim_quantity(seller_money_stock.size)} and the buyer has ${Trace.sim_quantity(buyer_money_stock.size)}")
    seller_stock.demand+=transferred_stock
    buyer_stock.supply-=transferred_stock
    seller_stock.save()
    buyer_stock.save()
    if buyer.id!=seller.id: #!Bizarrely, the code below does not work if the seller and buyer are the same
        buyer_money_stock.size-=cost
        buyer_money_stock.save()    
        seller_money_stock.size+=cost
        seller_money_stock.save()
    Trace.enter(simulation,1,f"After trade, the seller now has ${Trace.sim_quantity(seller_money_stock.size)} and the buyer ${Trace.sim_quantity(buyer_money_stock.size)}")

#! Set the total value and price of all stocks and commodities from their sizes
#! and to set the initial capital of each industry.
#! rather than trying to keep track on the fly.
#! SEE ALSO the documentation for trade(), produce() and reproduce()
#TODO ideally we should do both, as a check.
def set_total_value_and_price(simulation):
    current_time_stamp=simulation.current_time_stamp
    Trace.enter(simulation,1,f"Calculate Total Values, Prices and initial capital in simulation {simulation} for user {simulation.user}")
    logger.info(f"Calculate Total Values, Prices and initial capital for  simulation {simulation} at time stamp {current_time_stamp}")
    stocks=Stock.objects.filter(time_stamp=current_time_stamp)
    Trace.enter(simulation,2,"First calculate the price and value of each individual stock")
    for stock in stocks:
        unit_price=stock.commodity.unit_price
        unit_value=stock.commodity.unit_value
        size=stock.size
        stock.value=size*unit_value
        stock.price=size*unit_price
        owner_name=stock.stock_owner_name
        stock.save()
        Trace.enter(simulation,4,f"Size of the stock of {Trace.sim_object(stock.commodity.name)} owned by {Trace.sim_object(owner_name)} is {Trace.sim_quantity(stock.size)}. Its value is {Trace.sim_quantity(stock.value)} and its price is {Trace.sim_quantity(stock.price)}")
    
    Trace.enter(simulation,2,"Now calculate the price and value of each commodity, by summing over the stocks of that commodity")
    for commodity in Commodity.objects.filter(time_stamp=simulation.current_time_stamp):
        commodity.total_value=0
        commodity.total_price=0
        commodity.size=0
        stocks=Stock.objects.filter(time_stamp=simulation.current_time_stamp,commodity=commodity)
        for stock in stocks:
            commodity.total_value+=stock.value
            commodity.total_price+=stock.price
            commodity.size+=stock.size
        commodity.save()
        Trace.enter(simulation,3,f"Total size of commodity {Trace.sim_object(stock.commodity.name)} is {Trace.sim_quantity(commodity.size)}. Its value is {Trace.sim_quantity(commodity.total_value)} and its price is {Trace.sim_quantity(commodity.total_price)}")
    #! BOTH unit price and unit value may now have changed
    #! Therefore we:
    #* calculate these unit values and prices
    #* recalculate the value and price of each stock
    Trace.enter(simulation,2,"Now unit prices and values have changed. Recalculate them by dividing total price and value by the size, for each commodity")
    for commodity in Commodity.objects.filter(time_stamp=simulation.current_time_stamp):
        Trace.enter(simulation,3, f"There are now {Trace.sim_quantity(commodity. size)} units of Commodity {Trace.sim_object(commodity.name)} with total value {Trace.sim_quantity(commodity.total_value)} and total price {Trace.sim_quantity(commodity.total_price)}")
        if commodity.size!=0:
            new_unit_value=commodity.total_value/commodity.size
            new_unit_price=commodity.total_price/commodity.size
        else:
            Trace.enter(simulation,0,f"Note that the size of {commodity.name} is zero")
            logger.warning(f"In simulation{simulation}, commodity {commodity.name} has zero size")
            new_unit_value=1
            new_unit_price=1
        Trace.enter(simulation, 3,f"Unit value {Trace.sim_quantity(commodity.unit_value)} will be reset to {Trace.sim_quantity(new_unit_value)} and unit price {Trace.sim_quantity(commodity.unit_price)} and will be reset to {Trace.sim_quantity(new_unit_price)}")
        commodity.unit_value=new_unit_value
        commodity.unit_price=new_unit_price
        commodity.save()
    #! Now we have to revalue and reprice all stocks
    Trace.enter(simulation,2,"Now revalue stocks, using these unit values and prices")
    for stock in Stock.objects.filter(time_stamp=simulation.current_time_stamp):
        unit_price=stock.commodity.unit_price
        unit_value=stock.commodity.unit_value
        Trace.enter(simulation,4,f"Size of {Trace.sim_object(stock.commodity.name)} owned by {Trace.sim_object(stock.stock_owner_name)} is {Trace.sim_quantity(stock.size)}, with value {Trace.sim_quantity(stock.value)} and price {Trace.sim_quantity(stock.price)}")
        new_value=stock.size*unit_value
        new_price=stock.size*unit_price
        Trace.enter(simulation,4,f"Unit value is now {Trace.sim_quantity(unit_value)} so total value be reset to {Trace.sim_quantity(new_value)}; Unit price {Trace.sim_quantity(unit_price)} so total price will be reset to {Trace.sim_quantity(new_price)}")
        stock.value=new_value
        stock.price=new_price
        stock.save()

def set_initial_capital(simulation):
    #! Calculate the initial capital of each industry
    #! After production, we will then be able to calculate the profit

    #! THE BELOW DOES NOT WORK. FIND OUT WHY
    # for stock in IndustryStock.objects.filter(time_stamp=current_time_stamp):
    #     #!everybody owns somebody
    #     this_owner=stock.industry
    #     Trace.enter(simulation,1,f"trying to revalue capital of {this_owner.name} from stock of type {stock.usage_type} with price {stock.price}")
    #     if stock.price==0:
    #         Trace.enter(simulation,1,f"Stock has zero price; will not add it because of weird django error that resets initial capital to zero if zero is added to it")
    #     else:
    #         this_owner.initial_capital=this_owner.initial_capital+stock.price
    #         Trace.enter(simulation,2,f"Adding {stock.price} from stock of type {stock.usage_type} to the initial capital of {this_owner.name} whose total capital is now {this_owner.initial_capital}")
    # #! once we've recalculated the initial capitals, we have to save them.
    # for industry in Industry.objects.filter(time_stamp=current_time_stamp):
    #     Trace.enter(simulation,1, f"saving industry {industry.name} whose capital is {industry.initial_capital}" )
    #     industry.save()

    user=simulation.user
    current_time_stamp=simulation.current_time_stamp
    simulation.initial_capital=0
    Trace.enter(simulation,1,f"Calculate initial capitals for user {user} studying {simulation} with time stamp {current_time_stamp}")
    logger.info(f"Calculate initial capitals for user {user} who is currently studying {simulation} with time stamp {current_time_stamp}")

    for industry in Industry.objects.filter(time_stamp=current_time_stamp):
        Trace.enter(simulation,2,f"calculating the initial capital of industry {industry.name}")
        capital=0
        work_in_progress=0
        for stock in industry.stock_set.filter(time_stamp=current_time_stamp):
            Trace.enter(simulation,3,f"Adding the price {Trace.sim_quantity(stock.price)} of the stock of {Trace.sim_object(stock.commodity.name)}, type {Trace.sim_object(stock.usage_type)}")
            capital+=stock.price
            if stock.usage_type==PRODUCTION:
                work_in_progress+=stock.price
        Trace.enter(simulation,2,f"capital is now {Trace.sim_quantity(capital)} and work in progress is now {Trace.sim_quantity(work_in_progress)}")
        industry.initial_capital=capital
        industry.current_capital=capital
        industry.work_in_progress=work_in_progress
        industry.save() 
        simulation.initial_capital+=industry.initial_capital
        Trace.enter(simulation,2,f"Economy-wide initialcapital hs grown to {Trace.sim_quantity(simulation.initial_capital)} ")
    Trace.enter(simulation,1,f"Economy-wide initialcapital is {Trace.sim_quantity(simulation.initial_capital)} ")

def set_current_capital(simulation):
    #! Calculate the current capital of each industry and thence of the whole economy
    Trace.enter(simulation,1,f"Calculate current capitals")
    simulation.current_capital=0
    simulation.profit=0
    simulation.profit_rate=0
    for industry in Industry.objects.filter(time_stamp=simulation.current_time_stamp):
        Trace.enter(simulation,2,f"calculating the current capital of industry {Trace.sim_object(industry.name)}")
        capital=0
        work_in_progress=0
        for stock in industry.stock_set.filter(time_stamp=simulation.current_time_stamp):
            capital+=stock.price
            if stock.usage_type==PRODUCTION:
                work_in_progress+=stock.price
            Trace.enter(simulation,3,f"Adding the price {Trace.sim_quantity(stock.price)} of stock of {Trace.sim_object(stock.commodity.name)}, type {Trace.sim_object(stock.usage_type)}. Work in progress is {Trace.sim_quantity(work_in_progress)} and capital is {Trace.sim_quantity(capital)} ")
        industry.current_capital=capital
        industry.profit=capital-industry.initial_capital
        simulation.current_capital+=capital
        simulation.profit+=industry.profit
        if industry.initial_capital<=0:
            raise Exception(f"The initial capital of industry {industry} has not been correctly set")
        else:
            industry.profit_rate=(industry.profit/industry.initial_capital)*100
        Trace.enter(simulation,2,f"Current capital of industry {Trace.sim_object(industry.name)} is {Trace.sim_quantity(industry.current_capital)}; initial capital is {Trace.sim_quantity(industry.initial_capital)}; profit is {Trace.sim_quantity(industry.profit)}")
        Trace.enter(simulation, 2, f"Economy wide capital has grown to {Trace.sim_object(simulation.current_capital)} and profit to {Trace.sim_object(simulation.profit)}")
        industry.work_in_progress=work_in_progress
        industry.save()
    simulation.profit_rate=simulation.profit/simulation.initial_capital
    Trace.enter(simulation, 1, f"Economy wide capital is {Trace.sim_object(simulation.current_capital)}, profit is {Trace.sim_object(simulation.profit)} and the profit rate is {Trace.sim_object(simulation.profit_rate)}")

