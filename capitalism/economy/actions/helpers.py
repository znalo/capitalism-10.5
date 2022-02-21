from economy.models.report import Trace
from economy.models.commodity import Commodity
from economy.models.owners import Industry
from economy.models.stocks import Stock, IndustryStock
from ..global_constants import *
import inspect

def evaluate_stocks(simulation):
#! Set the price and value of every stock from its size
    frame, filename, ln, fn, lolc, idx=inspect.getouterframes(inspect.currentframe())[1]
    logger.info(f"evaluate stocks was called in simulation {simulation.name} from {filename}.{ln}.{fn}")

    Trace.enter(simulation,1,f"Evaluate stock values and prices from commodity unit prices and values")
    logger.info(f"Calculate values and prices for simulation {simulation} and time stamp  {simulation.current_time_stamp}")
    for stock in Stock.objects.filter(time_stamp=simulation.current_time_stamp):
        owner=stock.stock_owner
        verbs=owner.verbs()
        Trace.enter(simulation,3,f"{Trace.o(owner.name)} {verbs[5]} a stock of {Trace.o(stock.commodity.name)} whose size is presently {Trace.q(stock.size)}, with value {Trace.q(stock.value)} and price {Trace.q(stock.price)}")
        stock.value=stock.size*stock.commodity.unit_value
        stock.price=stock.size*stock.commodity.unit_price
        Trace.enter(simulation,4,f"Unit value is {Trace.q(stock.commodity.unit_value)} so total value has been reset to {Trace.q(stock.value)}")
        Trace.enter(simulation,4,f"Unit price {Trace.q(stock.commodity.unit_price)} so total price has been reset to {Trace.q(stock.price)}")
        stock.save()

"""
Calculate_commodity_totals adds up stock sizes, prices and values.
If there are **kwargs it will only check the totals, without changing them
"""
def calculate_commodity_totals(simulation,*args):
    frame, filename, ln, fn, lolc, idx=inspect.getouterframes(inspect.currentframe())[1]
    logger.info(f"calculate_commodity_totals was called in simulation {simulation.name} from {filename}.{ln}.{fn}")
    current_time_stamp=simulation.current_time_stamp
    Trace.enter(simulation,1,f"Calculate and/or check totals of commodity sizes, prices and values")
    logger.info(f"Calculate and/or check totals of commodity sizes, prices and values for simulation {simulation} at time stamp {current_time_stamp}")
    stocks=Stock.objects.filter(time_stamp=current_time_stamp)
    for commodity in Commodity.objects.filter(time_stamp=current_time_stamp):
        total_value=0
        total_price=0
        total_size=0
        stocks=Stock.objects.filter(time_stamp=current_time_stamp,commodity=commodity)
        for stock in stocks:
            total_value+=stock.value
            total_price+=stock.price
            total_size+=stock.size
            owner_name=stock.stock_owner.name
            Trace.enter(simulation,3,f"{Trace.o(owner_name)}'s stock of {Trace.o(stock.usage_type)} contains {Trace.q(stock.size)} with value {Trace.q(stock.value)} and price {Trace.q(stock.price)} of commodity {Trace.o(commodity.name)}")
        Trace.enter(simulation,2,f"Total size of commodity {Trace.o(stock.commodity.name)} is {Trace.q(total_size)}. Its value is {Trace.q(total_value)} and its price is {Trace.q(total_price)}")
        print(f"Calculate commodities was called with {len(args)} arguments")
        if len(args)==0:
            logger.info(f"Saving commodity {commodity.name} with size {total_size}, value {total_value} and price {total_price}")
            commodity.size, commodity.total_price, commodity.total_value=total_size,total_price,total_value
            commodity.save()
        else:
            message=""
            if total_size!=commodity.size:
                message=message+f" Size has changed from {commodity.size} to {total_size}" if "Checksize" in args  else message
            if total_value!=commodity.total_value:
                message=message+f" Value has changed from {commodity.total_value} to {total_value}" if "Checkvalue" in args  else message
            if total_price!=commodity.total_value:
                message=message+f" Price has changed from {commodity.total_price} to {total_price}" if "Checkprice" in args  else message
            if message=="":
                logger.info(f"Commodity {commodity.name} has not changed")
            else:
                logger.warning("Commodity {commodity.name} has changed as follows {message}")
    return

def evaluate_unit_prices_and_values(simulation):
    #! Set the size, unit price and value of each commodity to the average price and value of all stocks of it
    frame, filename, ln, fn, lolc, idx=inspect.getouterframes(inspect.currentframe())[1]
    logger.info(f"evaluate_unit_prices_and_values was called in simulation {simulation.name} from {filename}.{ln}.{fn}")
    current_time_stamp=simulation.current_time_stamp
    Trace.enter(simulation,1,f"Evaluate commodity prices and values")
    logger.info(f"Re-evaluate commodity prices and values for simulation {simulation} at time stamp {current_time_stamp}")

    Trace.enter(simulation,1,"Unit prices and values have changed. Recalculate them by dividing total price and value by the size, for each commodity")
    for commodity in Commodity.objects.filter(time_stamp=current_time_stamp):
        Trace.enter(simulation,2, f"There are now {Trace.q(commodity. size)} units of Commodity {Trace.o(commodity.name)} with total value {Trace.q(commodity.total_value)} and total price {Trace.q(commodity.total_price)}")
        if commodity.size!=0:
            new_unit_value=commodity.total_value/commodity.size
            new_unit_price=commodity.total_price/commodity.size
        else:
            Trace.enter(simulation,0,f"Note that the size of {commodity.name} is zero")
            logger.warning(f"In simulation{simulation}, commodity {commodity.name} has zero size")
            new_unit_value=1
            new_unit_price=1
        Trace.enter(simulation, 2,f"Unit value {Trace.q(commodity.unit_value)} has been reset to {Trace.q(new_unit_value)} and unit price {Trace.q(commodity.unit_price)} and will be reset to {Trace.q(new_unit_price)}")
        commodity.unit_value=new_unit_value
        commodity.unit_price=new_unit_price
        commodity.save()    

def set_initial_capital(simulation):
    frame, filename, ln, fn, lolc, idx=inspect.getouterframes(inspect.currentframe())[1]
    logger.info(f"set_initial_capital was called in simulation {simulation.name} from {filename}.{ln}.{fn}")
    user=simulation.user
    current_time_stamp=simulation.current_time_stamp
    current_time_stamp.initial_capital=0
    Trace.enter(simulation,1,f"Calculate initial capitals")
    logger.info(f"Calculate initial capitals for user {user} who is currently studying {simulation} with time stamp {current_time_stamp}")
    for industry in Industry.objects.filter(time_stamp=current_time_stamp):
        Trace.enter(simulation,2,f"calculating the initial capital of industry {industry.name}")
        capital=0
        work_in_progress=0
        stock_set=industry.stock_set.filter(time_stamp=current_time_stamp)
        for stock in stock_set:
            stock.refresh_from_db()
            Trace.enter(simulation,3,f"Adding the price ${Trace.q(stock.price)} of the stock of {Trace.o(stock.commodity.name)}, type {Trace.o(stock.usage_type)}")
            capital+=stock.price
            if stock.usage_type==PRODUCTION:
                work_in_progress+=stock.price
                Trace.enter(simulation,2,f"Initial work in progress is now ${Trace.q(work_in_progress)}")
        industry.initial_capital=capital
        industry.current_capital=capital
        industry.work_in_progress=work_in_progress
        industry.save() 
        current_time_stamp.initial_capital+=industry.initial_capital
        Trace.enter(simulation,2,f"Capital of {Trace.o(industry.name)} is now ${Trace.q(capital)}")        
        Trace.enter(simulation,2,f"Economy-wide initial capital so far is ${Trace.q(current_time_stamp.initial_capital)} ")
    current_time_stamp.current_capital=current_time_stamp.initial_capital
    current_time_stamp.profit=0
    current_time_stamp.profit_rate=0
    current_time_stamp.save()
    Trace.enter(simulation,1,f"Economy-wide initial capital is ${Trace.q(current_time_stamp.initial_capital)} ")

def set_current_capital(simulation):
    frame, filename, ln, fn, lolc, idx=inspect.getouterframes(inspect.currentframe())[1]
    logger.info(f"set_current_capital was called in simulation {simulation.name} from {filename}.{ln}.{fn}")
    Trace.enter(simulation,1,f"Calculate current capitals")
    current_time_stamp=simulation.current_time_stamp
    current_time_stamp.current_capital=0    
    current_time_stamp.profit=0
    current_time_stamp.profit_rate=0
    for industry in Industry.objects.filter(time_stamp=simulation.current_time_stamp):
        Trace.enter(simulation,2,f"calculating the current capital of industry {Trace.o(industry.name)}")
        capital=0
        work_in_progress=0
        for stock in industry.stock_set.filter(time_stamp=simulation.current_time_stamp):
            capital+=stock.price
            if stock.usage_type==PRODUCTION:
                work_in_progress+=stock.price
                Trace.enter(simulation,2,f"Current work in progress is now ${Trace.q(work_in_progress)}")
            Trace.enter(simulation,3,f"Adding the price {Trace.q(stock.price)} of stock of {Trace.o(stock.commodity.name)}, type {Trace.o(stock.usage_type)}. Work in progress is {Trace.q(work_in_progress)} and capital is {Trace.q(capital)} ")
        industry.current_capital=capital
        industry.profit=capital-industry.initial_capital
        current_time_stamp.current_capital+=capital
        current_time_stamp.profit+=industry.profit
        if industry.initial_capital<=0:
            raise Exception(f"The initial capital of industry {industry} has not been correctly set")
        else:
            industry.profit_rate=(industry.profit/industry.initial_capital)*100
        Trace.enter(simulation,2,f"Current capital of industry {Trace.o(industry.name)} is {Trace.q(industry.current_capital)}; initial capital is {Trace.q(industry.initial_capital)}; profit is {Trace.q(industry.profit)}")
        Trace.enter(simulation, 2, f"Economy wide capital has grown to {Trace.o(current_time_stamp.current_capital)} and profit to {Trace.o(current_time_stamp.profit)}")
        industry.work_in_progress=work_in_progress
        industry.save()
    current_time_stamp.profit_rate=current_time_stamp.profit/current_time_stamp.initial_capital*100
    current_time_stamp.save()
    Trace.enter(simulation, 1, f"Economy wide capital is {Trace.o(current_time_stamp.current_capital)}, profit is {Trace.o(current_time_stamp.profit)} and the profit rate is {Trace.o(current_time_stamp.profit_rate)}")

