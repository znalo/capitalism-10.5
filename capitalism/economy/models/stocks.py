from django.db import models
from economy.models.states import TimeStamp, Simulation
from economy.models.commodity import Commodity
from economy.global_constants import *
from economy.models.report import Trace

class Stock(models.Model): # Base class for IndustryStock and SocialStock
    time_stamp = models.ForeignKey(TimeStamp, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    commodity = models.ForeignKey(Commodity,  null=True, on_delete=models.CASCADE)
    usage_type = models.CharField( choices=USAGE_CHOICES, max_length=50, default=UNDEFINED) #! Sales, productive, consumption, money, sales
    owner_type = models.CharField(choices=STOCK_OWNER_TYPES, max_length=20,default=UNDEFINED)
    size = models.FloatField( default=0)
    stock_owner=models.ForeignKey("StockOwner",on_delete=models.CASCADE,null=True)
    value = models.FloatField( default=0)
    price = models.FloatField( default=0)
    demand=models.FloatField( default=0)
    supply=models.FloatField( default=0)
    monetary_demand=models.FloatField(default=0) #! Convenience field - should normally be simply set to demand * commodity.unit_price
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)

    @property
    def comparator_stock(self):
        comparator_time_stamp=self.simulation.comparator_time_stamp

        comparator_stocks=Stock.objects.filter(
            time_stamp=comparator_time_stamp,
            commodity__name=self.commodity.name,
            usage_type=self.usage_type,
            stock_owner__name=self.stock_owner.name,
            )
        if comparator_stocks.count()!=1:
            return self
        else:
            return comparator_stocks.get()

    @property
    def commodity_name(self):
        return self.commodity.name

    @property
    def owner_name(self):
        return self.stock_owner.name

    @property
    def display_order(self):
        return self.commodity.display_order

    @property
    def old_size(self):
        if self.comparator_stock==None:
            return -1
        else:
            last_size=self.comparator_stock.size
        return last_size

    @property
    def old_demand(self):
        if self.comparator_stock==None:
            return -1
        else:
            return self.comparator_stock.demand

    @property
    def old_supply(self):
        if self.comparator_stock==None:
            return -1
        else:
            return self.comparator_stock.supply

    @property
    def current_query_set(self):
        return Stock.objects.filter(self.simulation.current_time_stamp)

    #! TODO had to do this because {self} doesn't return __str__ for reasons I don't follow
    @property
    def description(self):
        return f"stock with owner:{self.stock_owner.name} commodity:{self.commodity.name} usage:{self.usage_type} id:{self.id}"


    def change_size(self,quantity):
    #! change the size of this stock by 'quantity'
    #! change its price using the commodity's unit price
    #! change its value using the commodity's unit value
    #! save self (NOTE caller does not have to do this) TODO is this the best way?
    #! tell the commodity about these changes
        logger.info(f"Stock {self.description} is changing its size by {quantity}")
        new_size=self.size+quantity
        new_price=self.price+quantity*self.commodity.unit_price
        new_value=self.value+quantity*self.commodity.unit_value
        if new_size<0 or new_value<0 or new_price<0:
            Trace.enter(self.simulation,0,"WARNING: the stock {self.commodity.name} of type {self.usage_type} owned by {self.stock_owner.name} will become negative with size {new_size}, value {new_value} and price {new_price}")
            # raise Exception (f"The stock {self} will become negative with size {new_size}, value {new_value} and price {new_price}")
        self.size=new_size
        self.price=new_price
        self.value=new_value
        self.commodity.change_size(quantity)
        self.save()
        return

class IndustryStock(Stock):
    industry = models.ForeignKey("Industry", on_delete=models.CASCADE, null=True) #TODO redundant? the base class has stock_owner
    production_requirement = models.FloatField( default=0)


    class Meta:
        verbose_name = 'Industry Stock'
        verbose_name_plural = 'Industry Stocks'


    def __str__(self):
        return f"[Project {self.time_stamp.simulation.project_number}]{self.owner_name}:{self.commodity.name}:{self.usage_type}[{self.id}]"


class SocialStock(Stock):
    social_class = models.ForeignKey("SocialClass",  related_name='class_stock', on_delete=models.CASCADE, null=True)
    consumption_requirement = models.FloatField(default=0)

    #! TODO had to do this because {self} doesn't return __str__ for reasons I don't follow

    class Meta:
        verbose_name = 'Social Stock'
        verbose_name_plural = 'Social Stocks'
        ordering = ['commodity__display_order']        

    def __str__(self):
        return f"[Project {self.time_stamp.simulation.project_number}]{self.social_class.name}:{self.commodity.name}:{self.usage_type}[{self.id}]"

