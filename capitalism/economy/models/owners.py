from django.db import models
from .states import TimeStamp, Simulation
from .report import Trace
from .commodity import Commodity
from .stocks import IndustryStock, Stock,SocialStock
from ..global_constants import *

class StockOwner(models.Model): # Base class for Industry and Social Class
    time_stamp = models.ForeignKey(TimeStamp, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default=UNDEFINED)
    commodity = models.ForeignKey(Commodity, related_name='%(app_label)s_%(class)s_related', on_delete=models.CASCADE)
    stock_owner_type=models.CharField(max_length=20,choices=STOCK_OWNER_TYPES,default=UNDEFINED)
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)

    def verbs(self):
        singulars=["is", "has", "wants", "sells", "doesn't", "owns"]
        plurals=["are", "have", "want", "sell", "don't", "own"]
        if self.stock_owner_type==INDUSTRY:
            return singulars
        else:
            return plurals

    @property
    def money_stock(self):
        stocks = Stock.objects.filter(time_stamp=self.time_stamp, usage_type=MONEY, stock_owner=self)
        if stocks.count()>1:
            logger.error(f"+++{self.name} has duplicate money stock") 
            return None
        elif stocks.count()==0:
            logger.error(f"+++{self.name} has no money stock") 
            return None
        return stocks.get()

    @property
    def sales_stock(self):
        stocks = Stock.objects.filter(time_stamp=self.time_stamp, usage_type=SALES, stock_owner=self)
        if stocks.count()>1:
            logger.error(f"+++{self.name} has duplicate sales stock") 
            return None
        elif stocks.count()==0:
            logger.error(f"+++{self.name} has no sales stock") 
            return None
        return stocks.get()

    @property
    def comparator_money_stock(self):
        return self.money_stock.comparator_stock

    @property
    def comparator_sales_stock(self):
        return self.sales_stock.comparator_stock

    @property
    def capitalists(self):
    #TODO generalise this so it is not hardwired
        try:
            capitalists_qs=SocialClass.objects.filter(time_stamp=self.time_stamp, name="Capitalists")
            capitalists=capitalists_qs.get()
        except Exception as error:
            logger.error(f"Too many capitalists for user {self.user} because of exception {error}. Giving Up")
            raise Exception("Too many capitalists. Cannot continue. This is either a data error or a programming error")
        return capitalists

class Industry(StockOwner):
# TODO subclass this properly see https://stackoverflow.com/questions/13347287/django-filter-base-class-by-child-class-names
    output_scale = models.IntegerField(verbose_name="Output", default=1)
    output_growth_rate = models.IntegerField(verbose_name="Growth Rate", default=1)
    initial_capital=models.FloatField(default=0)
    work_in_progress=models.FloatField(default=0)
    current_capital=models.FloatField(default=0)
    profit=models.FloatField(default=0)
    profit_rate=models.FloatField(default=0)

    class Meta:
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'

    @property
    def current_queryset(self):
        return Industry.objects.filter(time_stamp=self.user.current_simulation.current_time_stamp)

    @property
    def productive_stocks(self):
        return IndustryStock.objects.industrystock_set.filter(time_stamp=self.time_stamp,usage_type=PRODUCTION,industry=self)

    @property
    def replenishment_cost(self):
        #! calculate how much it will cost to purchase sufficient stocks for this industry to produce at its current scale
        simulation=self.simulation
        current_time_stamp=simulation.current_time_stamp
        #! Requires that demand is correctly set - this must be provided for by the caller 
        logger.info(f"Calculating replenishment cost for industry {self}")
        Trace.enter(simulation,3,f"Processing industry {Trace.o(self.name)}")
        cost=0
        productive_stocks=IndustryStock.objects.filter(usage_type=PRODUCTION,time_stamp=current_time_stamp,stock_owner=self)
        for stock in productive_stocks:
            cost+=stock.monetary_demand
            logger.info (f"Stock {stock} has found an additional cost of {stock.monetary_demand} and the cumulative total cost to {self.name} is now {cost}")
            Trace.enter(simulation,4,f"Industry {Trace.o(self.name)} has found an additional cost of {Trace.q(stock.monetary_demand)} and now needs a total of ${Trace.q(cost)} to replenish its stock of {Trace.o(stock.commodity_name)}")
        Trace.enter(simulation,3,f"The total money required by industry {Trace.o(self.name)} is {cost}")
        return cost

    @property
    def comparator(self):
        comparator_time_stamp=self.simulation.comparator_time_stamp
       
        comparator=Industry.objects.filter(
            time_stamp=comparator_time_stamp,
            name=self.name
            )
        if comparator.count()>1: #! primitive error-checking (there should be only and exactly one comparator) TODO more sophisticated error trapping
            return self
        elif comparator.count()<1:
            return None
        else:
            return comparator.first()    

    @property
    def comparator_initial_capital(self):
        return self.comparator.initial_capital

    @property
    def comparator_work_in_progress(self):
        return self.comparator.work_in_progress

    @property
    def comparator_current_capital(self):
        return self.comparator.current_capital

    @property
    def comparator_profit(self):
        return self.comparator.profit

    @property
    def comparator_profit_rate(self):
        return self.comparator.profit_rate

    # TODO this to be written. It will examine stocks to see what can actually be produced, given what we have.
    def scale_output(self):
        return 1

    def __str__(self):
        return self.name

class SocialClass(StockOwner):
    population = models.IntegerField(verbose_name="Population", default=1000)
    participation_ratio = models.FloatField(verbose_name="Participation Ratio", default=1)
    consumption_ratio = models.FloatField(verbose_name="Consumption Ratio", default=1)
    revenue = models.FloatField(verbose_name="Revenue", default=0)
    assets = models.FloatField(verbose_name="Assets", default=0)

    class Meta:
        verbose_name = 'Social Class'
        verbose_name_plural = 'Social Classes'

    @property
    def current_queryset(self):
        return SocialClass.objects.filter(time_stamp=self.user.current_simulation.current_time_stamp)

    def consumption_stocks(self):
        qs=SocialStock.objects.socialstock_set.filter(time_stamp=self.time_stamp,usage_type=CONSUMPTION,industry=self)
        return qs

    def __str__(self):
        return f"[Project {self.time_stamp.simulation.project_number}] {self.name}"

