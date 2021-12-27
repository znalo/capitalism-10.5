from django.db import models
from .states import TimeStamp, State
from .commodity import Commodity
from capitalism.global_constants import *

class Stock(models.Model): # Base class for IndustryStock and SocialStock
    time_stamp_FK = models.ForeignKey(TimeStamp, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    commodity_FK = models.ForeignKey(Commodity, verbose_name="Commodity", null=True, on_delete=models.CASCADE)
    usage_type = models.CharField(verbose_name="Stock Type", choices=USAGE_CHOICES, max_length=50, default=UNDEFINED) #! Sales, productive, consumption, money, sales
    owner_type = models.CharField(choices=STOCK_OWNER_TYPES, max_length=20,default=UNDEFINED)
    size = models.FloatField(verbose_name="Size", default=0)
    stock_owner_name = models.CharField(verbose_name="Owner Name",max_length=50, default=UNDEFINED)
    stock_owner_FK=models.ForeignKey("StockOwner",on_delete=models.CASCADE,null=True)
    value = models.FloatField(verbose_name="Value", default=0)
    price = models.FloatField(verbose_name="Price", default=0)
    demand=models.FloatField(verbose_name="Demand", default=0)
    supply=models.FloatField(verbose_name="Supply", default=0)
    owner = models.ForeignKey('auth.User', related_name='%(app_label)s_%(class)s_related', on_delete=models.CASCADE, default=1)

class IndustryStock(Stock):
    industry_FK = models.ForeignKey("Industry", verbose_name="Industry", on_delete=models.CASCADE, null=True)
    production_requirement = models.FloatField(verbose_name="Production Requirement", default=0)

    class Meta:
        verbose_name = 'Industry Stock'
        verbose_name_plural = 'Industry Stocks'

    def time_stamped_queryset():
        current_state=State.objects.get()
        qs=IndustryStock.objects.filter(time_stamp_FK=current_state.time_stamp_FK)
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

