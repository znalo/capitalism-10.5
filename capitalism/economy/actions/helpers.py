from economy.models.report import Trace
from economy.models.commodity import Commodity
from economy.models.owners import Industry, SocialClass, StockOwner
from economy.models.stocks import Stock, IndustryStock, SocialStock
from ..global_constants import *

def evaluate_stocks(simulation):
#! Set the price and value of every stock from its size and the unit price and value of its commodity
#! (Verify commodity total values and prices against unit values, prices and quantities of each commodity)
    Trace.enter(simulation,1,f"Evaluate stock values and prices from commodity unit prices and values")
    logger.info(f"Calculate values and prices for simulation {simulation} and time stamp  {simulation.current_time_stamp}")
    for stock in Stock.objects.filter(time_stamp=simulation.current_time_stamp):
        Trace.enter(simulation,4,f"{Trace.sim_object(stock.stock_owner.name)} owns a stock of {Trace.sim_object(stock.commodity.name)} whose size is presently {Trace.sim_quantity(stock.size)}, with value {Trace.sim_quantity(stock.value)} and price {Trace.sim_quantity(stock.price)}")
        stock.value=stock.size*stock.commodity.unit_value
        stock.price=stock.size*stock.commodity.unit_price
        Trace.enter(simulation,4,f"Unit value is {Trace.sim_quantity(stock.commodity.unit_value)} so total value has been reset to {Trace.sim_quantity(stock.value)}")
        Trace.enter(simulation,4,f"Unit price {Trace.sim_quantity(stock.commodity.unit_price)} so total price has been reset to {Trace.sim_quantity(stock.price)}")
        stock.save()

def evaluate_commodities(simulation):
#! Set the unit price and value of each commodity to the average price and value of all stocks of it
    current_time_stamp=simulation.current_time_stamp
    Trace.enter(simulation,1,f"Revalue commodity prices and values")
    logger.info(f"Revalue commodity prices and values for simulation {simulation} at time stamp {current_time_stamp}")
    
    stocks=Stock.objects.filter(time_stamp=current_time_stamp)
    for commodity in Commodity.objects.filter(time_stamp=current_time_stamp):
        commodity.total_value=0
        commodity.total_price=0
        commodity.size=0
        stocks=Stock.objects.filter(time_stamp=current_time_stamp,commodity=commodity)
        for stock in stocks:
            commodity.total_value+=stock.value
            commodity.total_price+=stock.price
            commodity.size+=stock.size
        commodity.save()
        Trace.enter(simulation,2,f"Total size of commodity {Trace.sim_object(stock.commodity.name)} is {Trace.sim_quantity(commodity.size)}. Its value is {Trace.sim_quantity(commodity.total_value)} and its price is {Trace.sim_quantity(commodity.total_price)}")
    Trace.enter(simulation,2,"Unit prices and values have changed. Recalculate them by dividing total price and value by the size, for each commodity")
    for commodity in Commodity.objects.filter(time_stamp=current_time_stamp):
        Trace.enter(simulation,3, f"There are now {Trace.sim_quantity(commodity. size)} units of Commodity {Trace.sim_object(commodity.name)} with total value {Trace.sim_quantity(commodity.total_value)} and total price {Trace.sim_quantity(commodity.total_price)}")
        if commodity.size!=0:
            new_unit_value=commodity.total_value/commodity.size
            new_unit_price=commodity.total_price/commodity.size
        else:
            Trace.enter(simulation,0,f"Note that the size of {commodity.name} is zero")
            logger.warning(f"In simulation{simulation}, commodity {commodity.name} has zero size")
            new_unit_value=1
            new_unit_price=1
        Trace.enter(simulation, 3,f"Unit value {Trace.sim_quantity(commodity.unit_value)} has been reset to {Trace.sim_quantity(new_unit_value)} and unit price {Trace.sim_quantity(commodity.unit_price)} and will be reset to {Trace.sim_quantity(new_unit_price)}")
        commodity.unit_value=new_unit_value
        commodity.unit_price=new_unit_price
        commodity.save()    

def set_initial_capital(simulation):
    #! Calculate the initial capital of each industry
    #! After production, we will then be able to calculate the profit
    user=simulation.user
    current_time_stamp=simulation.current_time_stamp
    current_time_stamp.initial_capital=0
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
        current_time_stamp.initial_capital+=industry.initial_capital
        Trace.enter(simulation,2,f"Economy-wide initialcapital hs grown to {Trace.sim_quantity(current_time_stamp.initial_capital)} ")
    current_time_stamp.current_capital=current_time_stamp.initial_capital
    current_time_stamp.profit=0
    current_time_stamp.profit_rate=0
    current_time_stamp.save()
    Trace.enter(simulation,1,f"Economy-wide initial capital is {Trace.sim_quantity(current_time_stamp.initial_capital)} ")

def set_current_capital(simulation):
    #! Calculate the current capital of each industry and thence of the whole economy
    Trace.enter(simulation,1,f"Calculate current capitals")
    current_time_stamp=simulation.current_time_stamp
    current_time_stamp.current_capital=0    
    current_time_stamp.profit=0
    current_time_stamp.profit_rate=0
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
        current_time_stamp.current_capital+=capital
        current_time_stamp.profit+=industry.profit
        if industry.initial_capital<=0:
            raise Exception(f"The initial capital of industry {industry} has not been correctly set")
        else:
            industry.profit_rate=(industry.profit/industry.initial_capital)*100
        Trace.enter(simulation,2,f"Current capital of industry {Trace.sim_object(industry.name)} is {Trace.sim_quantity(industry.current_capital)}; initial capital is {Trace.sim_quantity(industry.initial_capital)}; profit is {Trace.sim_quantity(industry.profit)}")
        Trace.enter(simulation, 2, f"Economy wide capital has grown to {Trace.sim_object(current_time_stamp.current_capital)} and profit to {Trace.sim_object(current_time_stamp.profit)}")
        industry.work_in_progress=work_in_progress
        industry.save()
    current_time_stamp.profit_rate=current_time_stamp.profit/current_time_stamp.initial_capital
    current_time_stamp.save()
    Trace.enter(simulation, 1, f"Economy wide capital is {Trace.sim_object(current_time_stamp.current_capital)}, profit is {Trace.sim_object(current_time_stamp.profit)} and the profit rate is {Trace.sim_object(current_time_stamp.profit_rate)}")

