from ..models.states import State, Log
from ..models.commodity import Commodity
from ..models.owners import Industry, SocialClass, StockOwner
from ..models.stocks import Stock, IndustryStock, SocialStock
from ..helpers import get_economy_view_context
from django.http import HttpResponse
from django.template import loader
from capitalism.global_constants import *

#! Calculate the unconstrained demand for all stocks
#! Use this to calculate the total demand for each commodity
#! Later (in 'allocate') we impose constraints arising from supply and (TODO) money shortages
def calculate_demand(request):
    if request.method == 'POST':
        Log.enter(0,'+++ACTION ERROR+++') #! crude test
        return HttpResponse("Programming error - I got a POST request and expected a GET")
    else:
        Log.enter(1,"Calculate Demand")
        current_state = State.objects.get(name="Initial")
        productive_stocks = IndustryStock.objects.filter(usage_type=PRODUCTION,time_stamp_FK=current_state.time_stamp_FK)
        social_stocks = SocialStock.objects.filter(time_stamp_FK=current_state.time_stamp_FK).exclude(usage_type=MONEY).exclude(usage_type=SALES)
        commodities = Commodity.objects.filter(time_stamp_FK=current_state.time_stamp_FK).exclude(usage=MONEY)

        for commodity in commodities:
            commodity.demand = 0
            commodity.save()

        for stock in productive_stocks:
            turnover_time = stock.commodity_FK.turnover_time
            stock.demand = stock.production_requirement*turnover_time
            stock.save()
            commodity = stock.commodity_FK
            commodity.demand += stock.demand
            Log.enter(2,f"{stock.stock_owner_name}'s stock of {stock.commodity_FK.name} is {stock.size}; production requirement is {stock.production_requirement} and turnover time is {turnover_time}. Demand is increased by {stock.demand} to {commodity.demand}")
            commodity.save()

        for stock in social_stocks:
            social_class = stock.social_class_FK
            stock.consumption_requirement = social_class.population*social_class.consumption_ratio
            stock.demand = stock.consumption_requirement
            commodity = stock.commodity_FK
            stock.save()
            commodity.demand += stock.demand
            Log.enter(2,f"{stock.social_class_FK.name}'s  demand for {stock.commodity_FK.name} is increased by {stock.demand} and is now {commodity.demand}")
            commodity.save()

        template = loader.get_template('economy/economy.html')
        context = get_economy_view_context({})
        return HttpResponse(template.render(context, request))

# TODO abstract the rendering into a single function

def calculate_supply(request):
    if request.method == 'POST':
        Log.enter(0,'+++ACTION ERROR+++')
        return HttpResponse("Programming error - I got a POST request and expected a GET")
    else:
        Log.enter(1,"Calculate supply")
        current_state = State.objects.get(name="Initial")
        #! Initialize every commodity's supply field to zero, prior to recalculating it from sales stocks
        commodities = Commodity.objects.filter(time_stamp_FK=current_state.time_stamp_FK).exclude(usage=MONEY)
        for commodity in commodities:
            commodity.supply = 0
            commodity.save()
        #! Calculate aggregate individual supply from the sales stocks and assign it to the appropriate commodity's supply field
        stocks = Stock.objects.filter( time_stamp_FK=current_state.time_stamp_FK,usage_type=SALES)
        for stock in stocks:
            commodity = stock.commodity_FK
            #? at this point supply is the same as the stock size, but may get scaled down if global supply is excessive
            stock.supply = stock.size
            stock.save()
            commodity.supply += stock.supply
            Log.enter(2,f" Supply of {commodity.name} from the industry {stock.stock_owner_name} is {stock.size}. Total supply is now {commodity.supply}")
            commodity.save()

        template = loader.get_template('economy/economy.html')
        context = get_economy_view_context({})
        return HttpResponse(template.render(context, request))

def allocate_supply(request):
    if request.method == 'POST':
        Log.enter(0,'+++ACTION ERROR+++')
        return HttpResponse("Programming error - I got a POST request and expected a GET")
    else:
        Log.enter(1,"Allocate demand depending on supply")
        current_state = State.objects.get(name="Initial")
        commodities = Commodity.objects.filter(time_stamp_FK=current_state.time_stamp_FK).exclude(usage=MONEY)
        for commodity in commodities:
            Log.enter(2,f" Allocating supply for commodity {commodity.name} whose supply is {commodity.supply} and demand is {commodity.demand}")
            if commodity.supply > 0:
            #! round to avoid silly float errors
                commodity.allocation_ratio = round(commodity.demand/commodity.supply, 4)
                Log.enter(3,f" Allocation ratio is {commodity.allocation_ratio}")
            if commodity.demand>commodity.supply: # demand is greater than supply, reduce it
                commodity.demand=commodity.supply
                Log.enter(3,f" Demand was greater than supply and is reduced to commodity.demand")
            commodity.save()

            related_stocks = commodity.stock_set.filter(time_stamp_FK=current_state.time_stamp_FK)
            for stock in related_stocks:
                Log.enter(2,f"Processing stock owned by {stock.stock_owner_name} of type {stock.usage_type} which has demand {stock.demand} and supply {stock.size}")
                if commodity.allocation_ratio>1: # demand is greater than supply, reduce it
                    stock.demand=stock.demand/commodity.allocation_ratio
                    Log.enter(3,f"This stock's demand cannot be satisfied, and is reduced to {stock.demand}")
                    stock.save()
                else:
                    Log.enter(3,"The demand for this commodity is equal to its supply, so this stock's demand is unchanged")

        template = loader.get_template('economy/economy.html')
        context = get_economy_view_context({})
        return HttpResponse(template.render(context, request))
#!TODO work out a way to use class abstraction to reduce the next two functions to one function

def sale(seller_stock, buyer_stock, seller, buyer):
    transferred_stock=min(buyer_stock.demand,seller_stock.supply)
    commodity=buyer_stock.commodity_FK
    cost=transferred_stock*commodity.unit_price
    seller_stock.size-=transferred_stock
    buyer_stock.size+=transferred_stock
    seller_stock.demand+=transferred_stock
    buyer_stock.supply-=transferred_stock
    seller_money_stock=seller.money_stock()
    buyer_money_stock=buyer.money_stock()
    seller_money_stock.size+=cost
    buyer_money_stock.size-=cost
    seller_stock.save()
    buyer_stock.save()
    seller_money_stock.save()
    buyer_money_stock.save()    
    Log.enter(3,f"Sale of {transferred_stock} at a cost of {cost} has taken place")

#! when all commodities have traded, set the total value and price of all stocks and commodities from their sizes
#! rather than trying to keep track on the fly.
#TODO ideally we should do both, as a check.
def set_total_value_and_price():
        Log.enter(1,"Calculate Total Values and Prices")
        current_state = State.objects.get(name="Initial")
        stocks=Stock.objects.filter(time_stamp_FK=current_state.time_stamp_FK)
        for stock in stocks:
            unit_price=stock.commodity_FK.unit_price
            unit_value=stock.commodity_FK.unit_value
            size=stock.size
            stock.value=size*unit_value
            stock.price=size*unit_price
            owner_name=stock.stock_owner_name
            stock.save()
            Log.enter(4,f"Value of the stock of {stock.commodity_FK.name} owned by {owner_name} is {stock.value} and its price is {stock.price}")
        for commodity in Commodity.objects.filter(time_stamp_FK=current_state.time_stamp_FK):
            total_value=0
            total_price=0
            stocks=Stock.objects.filter(time_stamp_FK=current_state.time_stamp_FK,commodity_FK=commodity)
            for stock in stocks:
                commodity.total_value+=stock.value
                commodity.total_price+=stock.price
            commodity.save()
            Log.enter(4,f"Total value of the stock of {stock.commodity_FK.name} is {commodity.total_value} and its total price is {commodity.total_price}")


def trade(request):
    Log.enter(0,"TRADE")
    Log.enter(1,"Industries")
    current_state = State.objects.get(name="Initial")

#! iterate over all stocks that want to buy something
    buyer_stocks=Stock.objects.filter(time_stamp_FK=current_state.time_stamp_FK).exclude(usage_type=MONEY).exclude(usage_type=SALES)
    for buyer_stock in buyer_stocks:
        buyer=buyer_stock.stock_owner_FK
        buyer_commodity=buyer_stock.commodity_FK
        Log.enter(2,f"{buyer.name} seeks to purchase {buyer_stock.demand} of {buyer_commodity.name} for its stock used for {buyer_commodity.usage} whose origin is {buyer_commodity.origin}")
        buyer_money_stock=buyer.money_stock()
        Log.enter(2,f"The buyer has {buyer_money_stock.size} in money and the unit price is {buyer_commodity.unit_price}. Looking for sellers")
        
        if buyer_commodity.origin=="SOCIAL":
            Log.enter(3,"This is a social stock")
        elif buyer_commodity.origin=="INDUSTRIAL":
            Log.enter(3,"This is an industrial stock")
        else:
            Log.enter(0,"+++UNKNOWN ORIGIN TYPE")

#! iterate over all potential sellers of this commodity
        potential_sellers=StockOwner.objects.filter(time_stamp_FK=current_state.time_stamp_FK)

        for seller in potential_sellers:
            seller_name=seller.name
            seller_stock=seller.sales_stock()
            seller_commodity=seller_stock.commodity_FK
            Log.enter(1,f"{seller_name} can offer {seller_stock.supply} of {seller_commodity} for sale to {buyer} who wants {buyer_commodity}")
            if seller_commodity==buyer_commodity:
                sale(seller_stock,buyer_stock,seller,buyer)

#!The below does not work. TODO find out why
        # sellers=potential_sellers.filter(commodity_FK=buyer_commodity) #! this returns an empty query, but only for social classes. No idea why.
        # for seller in sellers:
        #     seller_name=seller.name
        #     seller_stock=seller.sales_stock()
        #     seller_commodity=seller_stock.commodity_FK
        #     Log.enter(3,f"Owner {seller_name} can sell {seller_commodity.name} of which it has {seller_stock.supply}")
        #     sale(seller_stock,buyer_stock,seller,buyer)

    set_total_value_and_price()
    template = loader.get_template('economy/economy.html')
    context = get_economy_view_context({})
    return HttpResponse(template.render(context, request))

