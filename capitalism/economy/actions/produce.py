from ..global_constants import *
from economy.actions.helpers import set_current_capital
from economy.models.report import Trace
from economy.models.commodity import Commodity
from economy.models.owners import Industry, SocialClass
from economy.models.stocks import Stock, IndustryStock, SocialStock

#! Actions for the 'production' phase

def scale_output(industry):
#! scale output down if constrained by stock size. Normally should not happen, but we have to catch this to ensure stocks don't go negative
#TODO should this be a method of the Industry object?
    simulation=industry.user.current_simulation
    desired_scale=1
    scale_ratio=desired_scale
    #! first calculate the maximum scale at which this industry can operate, given the productive stocks it owns
    for productive_stock in IndustryStock.objects.all().filter(industry=industry,usage_type=PRODUCTION):
        if productive_stock.production_requirement*scale_ratio>productive_stock.size:
            scale_ratio=productive_stock.size/productive_stock.production_requirement
            Trace.enter(simulation,3,f"Insufficient stock of {productive_stock.commodity.name}; reducing scale by factor of {scale_ratio}")
    #! now we know the scale at which we can operate, reset the production requirements of all the productive stocks
    for productive_stock in IndustryStock.objects.filter(industry=industry):
        productive_stock.production_requirement*=scale_ratio
    #! reset this industry's output scale
    industry.output_scale*=scale_ratio
    return scale_ratio #! probably superfluous

def produce(industry, simulation):
#! Produce for one industry. Invoked by 'calculate_production'
#! TODO should be a method of Industry class?    
    periods_per_year=simulation.periods_per_year
    output_commodity=industry.commodity
    logger.info(f"Industry {industry} is producing {output_commodity} in simulation {simulation} with {periods_per_year} periods per year")
    unit_price_of_output=output_commodity.unit_price
    sales_stocks=IndustryStock.objects.filter(industry=industry,usage_type=SALES)
    if sales_stocks.count()!=1:
        logger.error(f"industry {Trace.o(industry)} has the wrong number of sales stocks. It has {sales_stocks.count()}")
        raise Exception (f"Industry {Trace.o(industry)} has the wrong number of sales stocks. It has {sales_stocks.count()}")
    sales_stock=sales_stocks.get()
    added_value=0
    for ps in IndustryStock.objects.all().filter(industry=industry,usage_type=PRODUCTION):
        productive_commodity=ps.commodity
        used_up_quantity=ps.production_requirement/periods_per_year
        ps.change_size(-used_up_quantity)
        if productive_commodity.origin=="INDUSTRIAL":
            added_value+=used_up_quantity*productive_commodity.unit_price
        elif productive_commodity.origin=="SOCIAL": #! assume it's labour power - alternative models may want to add other sources of value
            added_value+=used_up_quantity
        else:
            raise Exception (f"+++Commodity {productive_commodity.name} has unknown origin+++")
        Trace.enter(simulation,2,f"{Trace.o(industry.name)}'s stock of {Trace.o(productive_commodity.name)} has been reduced by {Trace.q(used_up_quantity)} to {Trace.q(ps.size)}")
        Trace.enter(simulation,2,f"Society's stock of {Trace.o(productive_commodity.name)} has been reduced by {Trace.q(used_up_quantity)} to {Trace.q(productive_commodity.size)}")
    #! NOTE that we don't use 'change_quantity' to recalculate the value of sales, because this moves independently
    sales_stock.size+=industry.output_scale/periods_per_year
    sales_stock.value+=added_value
    sales_stock.price=sales_stock.size*unit_price_of_output
    sales_stock.save()
    Trace.enter(simulation,1,f"{Trace.o(industry.name)}'s sales stock of {Trace.o(output_commodity.name)} has grown by {Trace.q(industry.output_scale)} to {Trace.q(sales_stock.size)}." )
    Trace.enter(simulation,1,f"Its unit price is {Trace.q(unit_price_of_output)} so its price is now {Trace.q(sales_stock.price)}. Its value is now {Trace.q(sales_stock.value)}")
  
def calculate_production(simulation):
    current_time_stamp=simulation.current_time_stamp
    #! establish the scale at which production is possible, given the stocks available
    for industry in Industry.objects.filter(time_stamp=current_time_stamp):
        ratio=industry.scale_output()
        Trace.enter(simulation,1,f"{industry}'s output will be scaled by {Trace.q(ratio)} and so will produce {Trace.q(industry.output_scale)} units of {Trace.o(industry.commodity.name)}")
    #! For each industry, carry out production
    for industry in Industry.objects.filter(time_stamp=current_time_stamp):
        produce(industry, simulation)
        industry.save()

"""
calculate the prices at which producers will sell products, and at which consumers will purchase them, when the production stage is complete.
it implements an algorithm determined by two parameters of the simulation that are specified either initially, or by the user:
 * price_response
 * melt_response
The first step is simply to register the values and prices that emerge from production.
Once this is done, there are three options (currently):
 * price_response_type==VALUES
   ** prices are simply set equal to values. Note that prices actually do have to be reset, because in general, the simulation may start with any arbitrary set of prices and values
 * price_response_type==EQUALIZED
   ** prices are set to proportions that equalise the profit rate. Note that this does not fully determine prices since the MELT may make them higher or lower in total than values
 * price_response_type==DYNAMIC
   ** prices are set in proportions that respond to differences between supply and demand
   ** as with EQUALIZED, the actual price level is determined by the melt_response parameter
Initially, in development, we suppose a melt-response of 1, that is, total money price=total price in labour time    Trace.enter(simulation,2,"RECALCULATING PRICES")
"""

def calculate_price_changes_in_distribution(simulation):
    current_time_stamp=simulation.current_time_stamp
    industries=Industry.objects.filter(simulation=simulation, time_stamp=current_time_stamp)
    if simulation.price_response_type=="EQUALIZED":
        Trace.enter(simulation,1,"EQUAL PROFIT RATE CALCULATION")
        r=simulation.current_time_stamp.profit_rate
        Trace.enter(simulation,2,f"General rate of profit is {r}")
        for industry in industries:
            commodity=industry.commodity
            x=commodity.size
            K=industry.initial_capital
            Trace.enter(simulation,2,f"Industry {industry} has sales stock {x} and initial capital {K}")
            desired_profit=(1+r/100)*K
            desired_unit_price=desired_profit/x
            Trace.enter(simulation,2,f"The unit price is {commodity.unit_price} and will be set to {desired_unit_price} ")
            commodity.unit_price=desired_unit_price
            commodity.save()
    return #! The caller must ensure that stocks are revalued

def calculate_reproduction(simulation):
#! Social Consumption
#! Production determines output values and prices
#! Once we have a sophisticated pricing model, prices will change as a result of reproduction (in response to demand, etc)
#! In any case, we suppose for simplicity a quantity-response model of social demand
#! So in the next stage (reproduction) classes set levels of consumption dependent on what they can afford
#! Then, in the sophisticated model, prices will respond to the changes in stocks. If stocks have fallen, prices will fall and vice versa.
    current_time_stamp=simulation.current_time_stamp
    periods_per_year=simulation.periods_per_year
    Trace.enter(simulation,0,f"Social Consumption")
    classes=SocialClass.objects.filter(time_stamp=current_time_stamp)
    for social_class in classes:
        Trace.enter(simulation,1, f"Social Class {social_class.name}")
        #! consumption determined by population and consumption ratio (and periods per year)
        #! (re-)production determined by participation_ratio (and periods per year)
        #! Both constrained by the stock at their disposal but more simply than for industries
        consumption_stocks=SocialStock.objects.filter(time_stamp=current_time_stamp, social_class=social_class,usage_type=CONSUMPTION)
        if consumption_stocks.count()<1:
            raise Exception(f"consumption stock of {social_class} does not exist")
        sales_stocks=SocialStock.objects.filter(time_stamp=current_time_stamp, social_class=social_class,usage_type=SALES)
        if sales_stocks.count()<1:
            raise Exception(f"Sales stock of {social_class} does not exist")
        elif sales_stocks.count()>1:
            raise Exception(f"Duplicate stock of {social_class}")
        else:
            sales_stock=sales_stocks.get()
            sales_amount=social_class.population*social_class.participation_ratio/periods_per_year
        if consumption_stocks.count()<1:
            raise Exception(f"consumption stock of {Trace.o(social_class.name)} does not exist")
        for cs in consumption_stocks: #! initial scaffold for multiplicity of consumption goods - needed for 3-sector model, etc, but will develop later
            quantity_consumed=cs.consumption_requirement
            if cs.size<quantity_consumed:
                Trace.enter(simulation,2,f"consumption by {Trace.o(social_class.name)} constrained to {Trace.q(cs.size)} because it does not have enough")
                quantity_consumed=cs.size/periods_per_year
            cs.size-=quantity_consumed
            sales_stock.size+=sales_amount
            sales_stock.save()
            cs.save()
            Trace.enter(simulation,1,f"Social Class {Trace.o(social_class.name)} have consumed {Trace.q(quantity_consumed)} and created {Trace.q(sales_amount)} of sales stocks")
            Trace.enter(simulation,1,f"{Trace.o(social_class.name)} now own {Trace.q(cs.size)} in consumption goods and have {Trace.q(sales_stock.size)} to sell")
