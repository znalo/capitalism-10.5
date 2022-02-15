from ..global_constants import *
from economy.actions.exchange import set_total_value_and_price, set_current_capital
from economy.models.report import Trace
from economy.models.commodity import Commodity
from economy.models.owners import Industry, SocialClass
from economy.models.stocks import Stock, IndustryStock, SocialStock

#! Actions for the 'production' phase

#! scale output down if constrained by stock size. Normally should not happen, but we have to catch this to ensure stocks don't go negative
#TODO should this be a method of the Industry object?
def scale_output(industry):
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

#! Produce for one industry. Invoked by 'calculate_production'
#! TODO should be a method of Industry class?
def produce(industry, simulation):
    periods_per_year=simulation.periods_per_year
    logger.info(f"Start production for Industry {industry} in simulation {simulation} with {periods_per_year} periods per year")
    sales_stocks=IndustryStock.objects.filter(industry=industry,usage_type=SALES)
    if sales_stocks.count()!=1:
        logger.error(f"industry {industry} has the wrong number of sales stocks. It has {sales_stocks.count()}")
        raise Exception (f"Industry {industry} has the wrong number of sales stocks. It has {sales_stocks.count()}")
    sales_stock=sales_stocks.get()
    unit_price_of_output=industry.commodity.unit_price
    added_value=0
    for ps in IndustryStock.objects.all().filter(industry=industry,usage_type=PRODUCTION):
        commodity=ps.commodity
        used_up_quantity=ps.production_requirement/periods_per_year
        ps.size-=used_up_quantity
        commodity.size-=used_up_quantity
        if commodity.origin=="INDUSTRIAL":
            added_value+=used_up_quantity*commodity.unit_price
        elif commodity.origin=="SOCIAL": #! assume it's labour power - alternative models may want to add other sources of value
            added_value+=used_up_quantity
        else:
            raise Exception (f"+++Commodity {commodity.name} has unknown origin+++")
        ps.save()
        Trace.enter(simulation,2,f"{industry.name}'s stock of {ps.commodity.name} has been reduced by {used_up_quantity} to {ps.size}")
        Trace.enter(simulation,2,f"Total social stock of {commodity.name}  has been reduced by {used_up_quantity} to {commodity.size}")
    sales_stock.size+=industry.output_scale/periods_per_year
    sales_stock.value+=added_value
    sales_stock.price=sales_stock.size*unit_price_of_output
    sales_stock.save()
    Trace.enter(simulation,1,f"{industry.name}'s sales stock has increased by {industry.output_scale} to {sales_stock.size} and its value has risen to {sales_stock.value}" )

def calculate_production(simulation):
    current_time_stamp=simulation.current_time_stamp
    Trace.enter(simulation,0,"Start Producing")
    #! establish the scale at which production is possible, given the stocks available
    for industry in Industry.objects.filter(time_stamp=current_time_stamp):
        ratio=industry.scale_output()
        Trace.enter(simulation,1,f"{industry}'s output will be scaled by {ratio} and so will produce {industry.output_scale} units of {industry.commodity.name}")
    #! For each industry, carry out production
    for industry in Industry.objects.filter(time_stamp=current_time_stamp):
        produce(industry, simulation)
        industry.save()
    Commodity.set_commodity_sizes(user=simulation.user)
    set_current_capital(simulation=simulation)    

#! Social Consumption
#! Production determines output values and prices
#! Once we have a sophisticated pricing model, prices will change as a result of reproduction (in response to demand, etc)
#! In any case, we suppose for simplicity a quantity-response model of social demand
#! So in the next stage (reproduction) classes set levels of consumption dependent on what they can afford
#! Then, in the sophisticated model, prices will respond to the changes in stocks. If stocks have fallen, prices will fall and vice versa.
def calculate_reproduction(simulation):
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
            raise Exception(f"consumption stock of {social_class} does not exist")
        for cs in consumption_stocks: #! initial scaffold for multiplicity of consumption goods - needed for 3-sector model, etc, but will develop later
            quantity_consumed=cs.consumption_requirement
            if cs.size<quantity_consumed:
                Trace.enter(simulation,2,f"consumption by {social_class} constrained to {cs.size} because it does not have enough")
                quantity_consumed=cs.size/periods_per_year
            cs.size-=quantity_consumed
            sales_stock.size+=sales_amount
            sales_stock.save()
            cs.save()
            Trace.enter(simulation,1,f"Social Class {social_class} has consumed {quantity_consumed} and created {sales_amount} of sales stocks")
            Trace.enter(simulation,1,f"{social_class} now owns {cs.size} in consumption goods and has {sales_stock.size} to sell")
