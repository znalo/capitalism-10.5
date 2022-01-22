from django.db import models
from .states import TimeStamp, State
from .report import Log
from .commodity import Commodity
from .stocks import IndustryStock, Stock,SocialStock
from ..global_constants import *
from .users import User

class StockOwner(models.Model): # Base class for Industry and Social Class
    time_stamp_FK = models.ForeignKey(TimeStamp, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default=UNDEFINED)
    commodity_FK = models.ForeignKey(Commodity, related_name='%(app_label)s_%(class)s_related', on_delete=models.CASCADE)
    stock_owner_type=models.CharField(max_length=20,choices=STOCK_OWNER_TYPES,default=UNDEFINED)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    class meta:
        ordering = ['time_stamp_FK.time_stamp']
    
    @property
    def money_stock(self):
        current_state = State.current_state()
        stocks = Stock.objects.filter(time_stamp_FK=State.current_stamp(), usage_type=MONEY, stock_owner_FK=self)
        if stocks.count()>1:
            Log(-1,f"+++{self.name} has duplicate money stock") #! TODO Log to raise an exception if entry is -1
            return None
        elif stocks.count()==0:
            Log(-1,f"+++{self.name} has no money stock") #! TODO Log to raise an exception if entry is -1
            return None
        return stocks.get()

    def sales_stock(self):
        current_state = State.objects.get(name="Initial")
        stocks = Stock.objects.filter(time_stamp_FK=State.current_stamp(), usage_type=SALES, stock_owner_FK=self)
        if stocks.count()>1:
            Log(-1,f"+++{self.name} has duplicate sales stock") #! TODO Log to raise an exception if entry is -1
            return None
        elif stocks.count()==0:
            Log(-1,f"+++{self.name} has no sales stock") #! TODO Log to raise an exception if entry is -1
            return None
        return stocks.get()
    #! unique method because it hardwires the name of the class.
    #TODO generalise this so it is not hardwired

    @staticmethod
    def capitalists():
        capitalists_qs=SocialClass.objects.filter(time_stamp_FK=State.current_stamp(), name="Capitalists")
        try:
            capitalists=capitalists_qs.get()
        except:
            raise Exception("Too many capitalists. Cannot continue. This is either a data error or a programming error")
        return capitalists

# TODO subclass this properly see https://stackoverflow.com/questions/13347287/django-filter-base-class-by-child-class-names
class Industry(StockOwner):
    output_scale = models.IntegerField(verbose_name="Output", default=1)
    output_growth_rate = models.IntegerField(verbose_name="Growth Rate", default=1)
    initial_capital=models.FloatField(default=0)
    work_in_progress=models.FloatField(default=0)
    current_capital=models.FloatField(default=0)
    profit=models.FloatField(default=0)
    profit_rate =models.FloatField(default=0)

    @staticmethod
    def current_queryset():
        return Industry.objects.filter(time_stamp_FK=State.current_stamp())

    def productive_stocks(self):
        return IndustryStock.objects.industrystock_set.filter(time_stamp_FK=State.current_stamp(),usage_type=PRODUCTION,industry_FK=self)

    #! calculate how much it will cost to purchase sufficient stocks for this industry to produce at its current scale
    def replenishment_cost(self):
        #! Requires that demand is correctly set - this must be provided for by the caller 
        productive_stocks = IndustryStock.objects.filter(usage_type=PRODUCTION,time_stamp_FK=State.current_stamp(),stock_owner_FK=self)
        cost=0
        for stock in productive_stocks:
            cost+=stock.monetary_demand
            Log.enter(2,f"Industry {Log.sim_object(self.name)} will need ${Log.sim_quantity(stock.monetary_demand)} to replenish its stock of {Log.sim_object(stock.commodity_name)}")
        Log.enter(2,f"The total money required by {Log.sim_object(self.name)} is {cost}")
        return cost

    def comparator(self):
        comparator_time_stamp=self.time_stamp_FK.comparator_time_stamp_FK
       
        comparator=Industry.objects.filter(
            time_stamp_FK=comparator_time_stamp,
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
        return self.comparator().initial_capital

    @property
    def comparator_work_in_progress(self):
        return self.comparator().work_in_progress

    @property
    def comparator_current_capital(self):
        return self.comparator().current_capital

    @property
    def comparator_profit(self):
        return self.comparator().profit

    @property
    def comparator_profit_rate(self):
        return self.comparator().profit_rate

    def __str__(self):
        return f"[Project {self.time_stamp_FK.project_FK.number}] {self.name}"

class SocialClass(StockOwner):
    population = models.IntegerField(verbose_name="Population", default=1000)
    participation_ratio = models.FloatField(verbose_name="Participation Ratio", default=1)
    consumption_ratio = models.FloatField(verbose_name="Consumption Ratio", default=1)
    revenue = models.FloatField(verbose_name="Revenue", default=0)
    assets = models.FloatField(verbose_name="Assets", default=0)

    class Meta:
        verbose_name = 'Social Class'
        verbose_name_plural = 'Social Classes'

    def time_stamped_queryset():
        qs=SocialClass.objects.filter(time_stamp_FK=State.current_stamp())
        return qs

    def consumption_stocks(self):
        qs=SocialStock.objects.socialstock_set.filter(time_stamp_FK=State.current_stamp(),usage_type=CONSUMPTION,industry_FK=self)
        return qs

    def __str__(self):
        return f"[Project {self.time_stamp_FK.project_FK.number}] {self.name}"

