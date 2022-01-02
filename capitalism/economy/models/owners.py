from django.db import models
from .states import TimeStamp, State, Log
from .commodity import Commodity
from capitalism.global_constants import STOCK_OWNER_TYPES,UNDEFINED
from .stocks import IndustryStock, Stock,SocialStock
from capitalism.global_constants import *

class StockOwner(models.Model): # Base class for Industry and Social Class
    time_stamp_FK = models.ForeignKey(TimeStamp, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default=UNDEFINED)
    commodity_FK = models.ForeignKey(Commodity, related_name='%(app_label)s_%(class)s_related', on_delete=models.CASCADE)
    stock_owner_type=models.CharField(max_length=20,choices=STOCK_OWNER_TYPES,default=UNDEFINED)
    owner = models.ForeignKey('auth.User', related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE, default=1)

    class meta:
        ordering = ['time_stamp_FK.time_stamp']

    def money_stock(self):
        current_state = State.objects.get(name="Initial")
        stocks = Stock.objects.filter(time_stamp_FK=current_state.time_stamp_FK, usage_type=MONEY, stock_owner_FK=self)
        if stocks.count()>1:
            Log(-1,f"+++{self.name} has duplicate money stock") #! TODO Log to raise an exception if entry is -1
            return None
        elif stocks.count()==0:
            Log(-1,f"+++{self.name} has no money stock") #! TODO Log to raise an exception if entry is -1
            return None
        return stocks.get()

    def sales_stock(self):
        current_state = State.objects.get(name="Initial")
        stocks = Stock.objects.filter(time_stamp_FK=current_state.time_stamp_FK, usage_type=SALES, stock_owner_FK=self)
        if stocks.count()>1:
            Log(-1,f"+++{self.name} has duplicate sales stock") #! TODO Log to raise an exception if entry is -1
            return None
        elif stocks.count()==0:
            Log(-1,f"+++{self.name} has no sales stock") #! TODO Log to raise an exception if entry is -1
            return None
        return stocks.get()

# TODO subclass this properly see https://stackoverflow.com/questions/13347287/django-filter-base-class-by-child-class-names
class Industry(StockOwner):
    output_scale = models.IntegerField(verbose_name="Output", default=1)
    output_growth_rate = models.IntegerField(verbose_name="Growth Rate", default=1)
    initial_capital=models.FloatField(default=0)
    work_in_progress=models.FloatField(default=0)
    current_capital=models.FloatField(default=0)
    profit=models.FloatField(default=0)
    profit_rate =models.FloatField(default=0)

    class Meta:
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'

    def time_stamped_queryset():
        current_state=State.objects.get()
        qs=Industry.objects.filter(time_stamp_FK=current_state.time_stamp_FK)
        return qs

    def productive_stocks(self):
        current_state=State.objects.get()
        qs=IndustryStock.objects.industrystock_set.filter(time_stamp_FK=current_state.time_stamp_FK,usage_type=PRODUCTION,industry_FK=self)
        return qs

    def comparator(self):
        comparator_time_stamp=self.time_stamp_FK.comparator_time_stamp_FK
       
        comparator=Industry.objects.filter(
            time_stamp_FK=comparator_time_stamp,
            name=self.name
            )
        if comparator.count()>1:
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
        profit_rate=self.comparator().profit_rate
        print (f"profit rate is {profit_rate}")
        return profit_rate


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
        current_state=State.objects.get()
        qs=SocialClass.objects.filter(time_stamp_FK=current_state.time_stamp_FK)
        return qs

    def consumption_stocks(self):
        current_state=State.objects.get()
        qs=SocialStock.objects.socialstock_set.filter(time_stamp_FK=current_state.time_stamp_FK,usage_type=CONSUMPTION,industry_FK=self)
        return qs

    def __str__(self):
        return f"[Project {self.time_stamp_FK.project_FK.number}] {self.name}"

