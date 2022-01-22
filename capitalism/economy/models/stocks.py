from django.db import models
from .states import TimeStamp, State
from .commodity import Commodity
from ..global_constants import *
from .users import User


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
    monetary_demand=models.FloatField(default=0) #! Conveninence field - should normally be simply set to demand * commodity.unit_price
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

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
    def old_size(self):
        if self.comparator_stock()==None:
            return -1
        else:
            last_size=self.comparator_stock().size
        return last_size

    @property
    def old_demand(self):
        if self.comparator_stock()==None:
            return -1
        else:
            return self.comparator_stock().demand

    @property
    def old_supply(self):
        if self.comparator_stock()==None:
            return -1
        else:
            return self.comparator_stock().supply


class IndustryStock(Stock):
    industry_FK = models.ForeignKey("Industry", verbose_name="Industry", on_delete=models.CASCADE, null=True)#TODO redundant? the base class has stock_owner_FK
    production_requirement = models.FloatField(verbose_name="Production Requirement", default=0)

    class Meta:
        verbose_name = 'Industry Stock'
        verbose_name_plural = 'Industry Stocks'

    def time_stamped_queryset():
        qs=IndustryStock.objects.filter(time_stamp_FK=State.current_stamp())
        return qs

    def __str__(self):
        return f"[Project {self.time_stamp_FK.project_FK.number}] [Industry {self.industry_FK.name}] [Commodity: {self.commodity_FK.name}] [Usage Type: {self.usage_type}]"


class SocialStock(Stock):
    social_class_FK = models.ForeignKey("SocialClass", verbose_name="Social Class", related_name='class_stock', on_delete=models.CASCADE, null=True)
    consumption_requirement = models.FloatField(verbose_name="Consumption Requirement", default=0)
    
    class Meta:
        verbose_name = 'Social Stock'
        verbose_name_plural = 'Social Stocks'

    def time_stamped_queryset():
        current_state=State.objects.get()
        qs=SocialStock.objects.filter(time_stamp_FK=current_state.time_stamp_FK)
        return qs

    def __str__(self):
        return f"[Project {self.time_stamp_FK.project_FK.number}] [Class {self.social_class_FK.name}] [Commodity: {self.commodity_FK.name}] [Usage Type: {self.usage_type}]"

