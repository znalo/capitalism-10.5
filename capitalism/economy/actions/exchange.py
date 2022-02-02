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
def calculate_demand(user):
    logger.info(f"Calculate demand for user {user}")
    Trace.enter(user,1,"Calculate Demand")
    productive_stocks = IndustryStock.objects.filter(usage_type=PRODUCTION,time_stamp_FK=user.current_time_stamp)
    social_stocks = SocialStock.objects.filter(time_stamp_FK=user.current_time_stamp).exclude(usage_type=MONEY).exclude(usage_type=SALES)
    commodities = Commodity.objects.filter(time_stamp_FK=user.current_time_stamp).exclude(usage=MONEY)

    for commodity in commodities:
        commodity.demand = 0
        commodity.save()

    for stock in productive_stocks:
        turnover_time = stock.commodity_FK.turnover_time
        stock.demand = stock.production_requirement*turnover_time
        stock.demand -= stock.size #! We only want to bring the stock size up to what is needed to produce at the current scale
        stock.monetary_demand=stock.demand*commodity.unit_price
        stock.save()
        commodity = stock.commodity_FK
        commodity.demand += stock.demand
        Trace.enter(user,2,f"{Trace.sim_object(stock.stock_owner_name)}'s stock of {Trace.sim_object(stock.commodity_FK.name)} is {Trace.sim_quantity(stock.size)}; production requirement is {Trace.sim_quantity(stock.production_requirement)} and turnover time is {Trace.sim_quantity(turnover_time)}. Demand is increased by {Trace.sim_quantity(stock.demand)} to {Trace.sim_quantity(commodity.demand)}")
        commodity.save()

    for stock in social_stocks:
        social_class = stock.social_class_FK
        stock.consumption_requirement = social_class.population*social_class.consumption_ratio
        stock.demand = stock.consumption_requirement
        stock.demand -= stock.size #! We only want to bring the stock size up to what is needed to produce at the current scale
        commodity = stock.commodity_FK
        stock.monetary_demand=stock.demand*commodity.unit_price
        stock.save()
        commodity.demand += stock.demand
        Trace.enter(user,2,f"{Trace.sim_object(stock.social_class_FK.name)}'s  demand for {Trace.sim_object(stock.commodity_FK.name)} is increased by {Trace.sim_quantity(stock.demand)} and is now {Trace.sim_quantity(commodity.demand)}")
        commodity.save()

# TODO abstract the rendering into a single function

def calculate_supply(user):
    logger.info(f"Calculate supply for user {user}")
    Trace.enter(user,1,"Calculate supply")
    #! Initialize every commodity's supply field to zero, prior to recalculating it from sales stocks
    commodities = Commodity.objects.filter(time_stamp_FK=user.current_time_stamp).exclude(usage=MONEY)
    for commodity in commodities:
        commodity.supply = 0
        commodity.save()
    #! Calculate aggregate individual supply from the sales stocks and assign it to the appropriate commodity's supply field
    stocks = Stock.objects.filter( time_stamp_FK=user.current_time_stamp,usage_type=SALES)
    for stock in stocks:
        commodity = stock.commodity_FK
        #? at this point supply is the same as the stock size, but may get scaled down if global supply is excessive
        stock.supply = stock.size
        stock.save()
        commodity.supply += stock.supply
        Trace.enter(user,2,f" Supply of {Trace.sim_object(commodity.name)} from the industry {Trace.sim_object(stock.stock_owner_name)} is {Trace.sim_quantity(stock.size)}. Total supply is now {Trace.sim_quantity(commodity.supply)}")
        commodity.save()

def calculate_demand_and_supply(user):
    logger.info(f"Calculate demand and supply for user {user}")
    calculate_demand(user=user)
    calculate_supply(user=user)

def allocate_supply(user):
    logger.info(f"Allocate supply for user {user}")
    Trace.enter(user,1,"Allocate demand depending on supply")
    commodities = Commodity.objects.filter(time_stamp_FK=user.current_time_stamp).exclude(usage=MONEY)
    for commodity in commodities:
        Trace.enter(user,2,f" Allocating supply for commodity {Trace.sim_object(commodity.name)} whose supply is {Trace.sim_quantity(commodity.supply)} and demand is {Trace.sim_quantity(commodity.demand)}")
        if commodity.supply > 0:
        #! round to avoid silly float errors
            commodity.allocation_ratio = round(commodity.demand/commodity.supply, 4)
            Trace.enter(user,3,f" Allocation ratio is {Trace.sim_object(commodity.allocation_ratio)}")
        if commodity.demand>commodity.supply: # demand is greater than supply, reduce it
            commodity.demand=commodity.supply
            Trace.enter(user,3,f" Demand was greater than supply and is reduced to commodity.demand")
        commodity.save()

        related_stocks = commodity.stock_set.filter(time_stamp_FK=user.current_time_stamp)
        for stock in related_stocks:
            if commodity.allocation_ratio>1: # demand is greater than supply, reduce it
                stock.demand=stock.demand/commodity.allocation_ratio
                Trace.enter(user,3,f"This stock's demand cannot be satisfied, and is reduced to {Trace.sim_quantity(stock.demand)}")
                stock.save()
            else:
                Trace.enter(user,3,"The demand for this commodity is equal to its supply, so this stock's demand is unchanged")

#!TODO work out a way to use class abstraction to reduce the next two functions to one function

def sale(seller_stock, buyer_stock, seller, buyer):
    user=seller.user #! TODO we might want to have a little consistency check that all objects have the same user
    transferred_stock=min(buyer_stock.demand,seller_stock.supply)
    commodity=buyer_stock.commodity_FK
    cost=transferred_stock*commodity.unit_price
    seller_stock.size-=transferred_stock
    buyer_stock.size+=transferred_stock
    seller_money_stock=seller.money_stock
    buyer_money_stock=buyer.money_stock
    Trace.enter(user,1,f"Sale: {Trace.sim_object(buyer.name)} is buying {Trace.sim_quantity(transferred_stock)} of {Trace.sim_object(seller_stock.commodity_FK.name)} from {Trace.sim_object(seller.name)} at a cost of {Trace.sim_quantity(cost)}")
    Trace.enter(user,1,f"The seller has ${Trace.sim_quantity(seller_money_stock.size)} and the buyer has ${Trace.sim_quantity(buyer_money_stock.size)}")
    seller_stock.demand+=transferred_stock
    buyer_stock.supply-=transferred_stock
    seller_stock.save()
    buyer_stock.save()
    if buyer.id!=seller.id: #!Bizarrely, the code below does not work if the seller and buyer are the same
        buyer_money_stock.size-=cost
        buyer_money_stock.save()    
        seller_money_stock.size+=cost
        seller_money_stock.save()
    Trace.enter(user,1,f"After trade, the seller now has ${Trace.sim_quantity(seller_money_stock.size)} and the buyer ${Trace.sim_quantity(buyer_money_stock.size)}")

#! Set the total value and price of all stocks and commodities from their sizes
#! and to set the initial capital of each industry.
#! rather than trying to keep track on the fly.
#! SEE ALSO the documentation for trade(), produce() and reproduce()
#TODO ideally we should do both, as a check.

def set_total_value_and_price(user):
    Trace.enter(user,1,"Calculate Total Values, Prices and initial capital")
    logger.info(f"Calculate Total Values, Prices and initial capital for user {user}")
    stocks=Stock.objects.filter(time_stamp_FK=user.current_time_stamp)
    Trace.enter(user,2,"First calculate the price and value of each individual stock")
    for stock in stocks:
        unit_price=stock.commodity_FK.unit_price
        unit_value=stock.commodity_FK.unit_value
        size=stock.size
        stock.value=size*unit_value
        stock.price=size*unit_price
        owner_name=stock.stock_owner_name
        stock.save()
        Trace.enter(user,4,f"Size of the stock of {Trace.sim_object(stock.commodity_FK.name)} owned by {Trace.sim_object(owner_name)} is {Trace.sim_quantity(stock.size)}. Its value is {Trace.sim_quantity(stock.value)} and its price is {Trace.sim_quantity(stock.price)}")
    Trace.enter(user,2,"Now calculate the price and value of each commodity, by summing over the stocks of that commodity")
    for commodity in Commodity.objects.filter(time_stamp_FK=user.current_time_stamp):
        commodity.total_value=0
        commodity.total_price=0
        commodity.size=0
        stocks=Stock.objects.filter(time_stamp_FK=user.current_time_stamp,commodity_FK=commodity)
        for stock in stocks:
            commodity.total_value+=stock.value
            commodity.total_price+=stock.price
            commodity.size+=stock.size
        commodity.save()
        Trace.enter(user,3,f"Total size of commodity {Trace.sim_object(stock.commodity_FK.name)} is {Trace.sim_quantity(commodity.size)}. Its value is {Trace.sim_quantity(commodity.total_value)} and its price is {Trace.sim_quantity(commodity.total_price)}")
    #! BOTH unit price and unit value may now have changed
    #! Therefore we:
    #* calculate these unit values and prices
    #* recalculate the value and price of each stock
    Trace.enter(user,2,"Now unit prices and values have changed. Recalculate them by dividing total price and value by the size, for each commodity")
    for commodity in Commodity.objects.filter(time_stamp_FK=user.current_time_stamp):
        Trace.enter(user,3, f"There are now {Trace.sim_quantity(commodity. size)} units of Commodity {Trace.sim_object(commodity.name)} with total value {Trace.sim_quantity(commodity.total_value)} and total price {Trace.sim_quantity(commodity.total_price)}")
        if commodity.size!=0:
            new_unit_value=commodity.total_value/commodity.size
            new_unit_price=commodity.total_price/commodity.size
        else:
            Trace.enter(user,0,f"Note that the size of {commodity.name} is zero")
            logger.warning(f"In the simulation belonging to {user}, commodity {commodity.name} has zero size")
            new_unit_value=1
            new_unit_price=1
        Trace.enter(user,3,f"Unit value {Trace.sim_quantity(commodity.unit_value)} will be reset to {Trace.sim_quantity(new_unit_value)} and unit price {Trace.sim_quantity(commodity.unit_price)} and will be reset to {Trace.sim_quantity(new_unit_price)}")
        commodity.unit_value=new_unit_value
        commodity.unit_price=new_unit_price
        commodity.save()
    #! Now we have to revalue and reprice all stocks
    Trace.enter(user,2,"Now revalue stocks, using these unit values and prices")
    for stock in Stock.objects.filter(time_stamp_FK=user.current_time_stamp):
        unit_price=stock.commodity_FK.unit_price
        unit_value=stock.commodity_FK.unit_value
        Trace.enter(user,4,f"Size of {Trace.sim_object(stock.commodity_FK.name)} owned by {Trace.sim_object(stock.stock_owner_name)} is {Trace.sim_quantity(stock.size)}, with value {Trace.sim_quantity(stock.value)} and price {Trace.sim_quantity(stock.price)}")
        new_value=stock.size*unit_value
        new_price=stock.size*unit_price
        Trace.enter(user,4,f"Unit value is now {Trace.sim_quantity(unit_value)} so total value be reset to {Trace.sim_quantity(new_value)}; Unit price {Trace.sim_quantity(unit_price)} so total price will be reset to {Trace.sim_quantity(new_price)}")
        stock.value=new_value
        stock.price=new_price
        stock.save()

def trade(user):
    Trace.enter(user,1,"TRADE")
    logger.info(f"User {user} is trading")
    Trace.enter(user,2,"Industries")
 
    #! iterate over all stocks that want to buy something
    buyer_stocks=Stock.objects.filter(time_stamp_FK=user.current_time_stamp).exclude(usage_type=MONEY).exclude(usage_type=SALES)
    for buyer_stock in buyer_stocks:
        buyer=buyer_stock.stock_owner_FK
        buyer_commodity=buyer_stock.commodity_FK
        Trace.enter(user,3,f"{Trace.sim_object(buyer.name)} seeks to purchase {Trace.sim_quantity(buyer_stock.demand)} of {Trace.sim_object(buyer_commodity.name)} for stock of usage type {Trace.sim_object(buyer_commodity.usage)} whose origin is {Trace.sim_object(buyer_commodity.origin)}")
        buyer_money_stock=buyer.money_stock
        Trace.enter(user,3,f"The buyer has {Trace.sim_quantity(buyer_money_stock.size)} in money and the unit price is {Trace.sim_quantity(buyer_commodity.unit_price)}. Looking for sellers")
        
        #! iterate over all potential sellers of this commodity
        potential_sellers=StockOwner.objects.filter(time_stamp_FK=user.current_time_stamp)

        for seller in potential_sellers:
            seller_name=seller.name
            seller_stock=seller.sales_stock
            seller_commodity=seller_stock.commodity_FK
            Trace.enter(user,3,f"{Trace.sim_object(seller_name)} can offer {Trace.sim_quantity(seller_stock.supply)} of {Trace.sim_object(seller_commodity.name)} for sale to {Trace.sim_object(buyer.name)} who wants {Trace.sim_object(buyer_commodity.name)}")
            if seller_commodity==buyer_commodity:
                sale(seller_stock,buyer_stock,seller,buyer)

        #!The below does not work. TODO find out why
        # sellers=potential_sellers.filter(commodity_FK=buyer_commodity) #! this returns an empty query, but only for social classes. No idea why.
        # for seller in sellers:
        #     seller_name=seller.name
        #     seller_stock=seller.sales_stock()
        #     seller_commodity=seller_stock.commodity_FK
        #     Trace.enter(user,3,f"Owner {seller_name} can sell {seller_commodity.name} of which it has {seller_stock.supply}")
        #     sale(seller_stock,buyer_stock,seller,buyer)

    #!Every industry now has the goods with which they will start production.
    #!At the end of this process, we (and the owners) want to know how much profit the industries have made
    #!Therefore, we now establish a couple of things
    #* What is the total value and price of each commodity?
    #* What is the total value and price of each stock?
    #* What is the total value and price of each industry?
    #* Note that though the total price of the assets of each owner will be unchanged by trade
    #* the value of these assets will - as a result of unequal exchange
    #* So we make this calculation both before and after production
    set_total_value_and_price(user=user)
    set_current_capital(user=user)
 
def set_initial_capital(user):
    #! Calculate the initial capital of each industry
    #! After production, we will then be able to calculate the profit

    #! THE BELOW DOES NOT WORK. FIND OUT WHY
    # for stock in IndustryStock.objects.filter(time_stamp_FK=current_time_stamp):
    #     #!everybody owns somebody
    #     this_owner=stock.industry_FK
    #     Trace.enter(user,1,f"trying to revalue capital of {this_owner.name} from stock of type {stock.usage_type} with price {stock.price}")
    #     if stock.price==0:
    #         Trace.enter(user,1,f"Stock has zero price; will not add it because of weird django error that resets initial capital to zero if zero is added to it")
    #     else:
    #         this_owner.initial_capital=this_owner.initial_capital+stock.price
    #         Trace.enter(user,2,f"Adding {stock.price} from stock of type {stock.usage_type} to the initial capital of {this_owner.name} whose total capital is now {this_owner.initial_capital}")
    # #! once we've recalculated the initial capitals, we have to save them.
    # for industry in Industry.objects.filter(time_stamp_FK=current_time_stamp):
    #     Trace.enter(user,1, f"saving industry {industry.name} whose capital is {industry.initial_capital}" )
    #     industry.save()
    Trace.enter(user,1,f"Calculate initial capitals")

    for industry in Industry.objects.filter(time_stamp_FK=user.current_time_stamp):
        Trace.enter(user,2,f"calculating the initial capital of industry {industry.name}")
        capital=0
        work_in_progress=0
        for stock in industry.stock_set.filter(time_stamp_FK=user.current_time_stamp):
            Trace.enter(user,3,f"Adding the price {Trace.sim_quantity(stock.price)} of the stock of {Trace.sim_object(stock.commodity_FK.name)}, type {Trace.sim_object(stock.usage_type)}")
            capital+=stock.price
            if stock.usage_type==PRODUCTION:
                work_in_progress+=stock.price
        Trace.enter(user,2,f"capital is now {Trace.sim_quantity(capital)} and work in progress is now {Trace.sim_quantity(work_in_progress)}")
        industry.initial_capital=capital
        industry.current_capital=capital
        industry.work_in_progress=work_in_progress
        industry.save() 


def set_current_capital(user):
    #! Calculate the current capital of each industry
    Trace.enter(user,1,f"Calculate current capitals")
    for industry in Industry.objects.filter(time_stamp_FK=user.current_time_stamp):
        Trace.enter(user,2,f"calculating the current capital of industry {Trace.sim_object(industry.name)}")
        capital=0
        work_in_progress=0
        for stock in industry.stock_set.filter(time_stamp_FK=user.current_time_stamp):
            capital+=stock.price
            if stock.usage_type==PRODUCTION:
                work_in_progress+=stock.price
            Trace.enter(user,3,f"Adding the price {Trace.sim_quantity(stock.price)} of stock of {Trace.sim_object(stock.commodity_FK.name)}, type {Trace.sim_object(stock.usage_type)}. Work in progress is {Trace.sim_quantity(work_in_progress)} and capital is {Trace.sim_quantity(capital)} ")
        industry.current_capital=capital
        industry.profit=capital-industry.initial_capital
        industry.profit_rate=(industry.profit/industry.initial_capital)*100
        Trace.enter(user,2,f"Current capital of industry {Trace.sim_object(industry.name)} is {Trace.sim_quantity(industry.current_capital)}; initial capital is {Trace.sim_quantity(industry.initial_capital)}; profit is {Trace.sim_quantity(industry.profit)}")
        industry.work_in_progress=work_in_progress
        industry.save()
