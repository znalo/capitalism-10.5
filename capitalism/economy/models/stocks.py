from django.db import models
from .states import TimeStamp, Simulation
from .commodity import Commodity
from ..global_constants import *


class Stock(models.Model): # Base class for IndustryStock and SocialStock
    time_stamp_FK = models.ForeignKey(TimeStamp, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    commodity_FK = models.ForeignKey(Commodity,  null=True, on_delete=models.CASCADE)
    usage_type = models.CharField( choices=USAGE_CHOICES, max_length=50, default=UNDEFINED) #! Sales, productive, consumption, money, sales
    owner_type = models.CharField(choices=STOCK_OWNER_TYPES, max_length=20,default=UNDEFINED)
    size = models.FloatField( default=0)
    stock_owner_name = models.CharField(max_length=50, default=UNDEFINED)
    stock_owner_FK=models.ForeignKey("StockOwner",on_delete=models.CASCADE,null=True)
    value = models.FloatField( default=0)
    price = models.FloatField( default=0)
    demand=models.FloatField( default=0)
    supply=models.FloatField( default=0)
    monetary_demand=models.FloatField(default=0) #! Convenience field - should normally be simply set to demand * commodity.unit_price
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)

    class meta:     #! helps view the objects in time stamp order in admin
        ordering = ['time_stamp_FK.time_stamp']

    @property
    def comparator_stock(self):
        comparator_time_stamp=self.time_stamp_FK.comparator_time_stamp_FK
        comparator_stock=Stock.objects.filter(
            time_stamp_FK=comparator_time_stamp,
            stock_owner_name=self.stock_owner_name,
            commodity_FK__name=self.commodity_FK.name,
            usage_type=self.usage_type
            )
        if comparator_stock.count()>1:
            return self
        elif comparator_stock.count()<1:
            return None
        else:
            return comparator_stock.first()

    @property
    def commodity_name(self):
        return self.commodity_FK.name

    @property
    def display_order(self):
        return self.commodity_FK.display_order

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
        return Stock.objects.filter(self.user.current_simulation.current_time_stamp)

class IndustryStock(Stock):
    industry_FK = models.ForeignKey("Industry", on_delete=models.CASCADE, null=True) #TODO redundant? the base class has stock_owner_FK
    production_requirement = models.FloatField( default=0)

    class Meta:
        verbose_name = 'Industry Stock'
        verbose_name_plural = 'Industry Stocks'

    def __str__(self):
        return f"[Project {self.time_stamp_FK.simulation_FK.project_number}] [Industry {self.industry_FK.name}] [Commodity: {self.commodity_FK.name}] [Usage Type: {self.usage_type}]"


class SocialStock(Stock):
    social_class_FK = models.ForeignKey("SocialClass",  related_name='class_stock', on_delete=models.CASCADE, null=True)
    consumption_requirement = models.FloatField(default=0)
    
    class Meta:
        verbose_name = 'Social Stock'
        verbose_name_plural = 'Social Stocks'
        ordering = ['commodity_FK__display_order']        

    def __str__(self):
        return f"[Project {self.time_stamp_FK.simulation_FK.project_number}] [Class {self.social_class_FK.name}] [Commodity: {self.commodity_FK.name}] [Usage Type: {self.usage_type}]"

