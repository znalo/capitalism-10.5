from django.db import models
from .states import TimeStamp, Simulation
from ..global_constants import ORIGIN_CHOICES, USAGE_CHOICES, UNDEFINED, logger
from .report import Trace

class Commodity(models.Model):
    time_stamp = models.ForeignKey(TimeStamp, related_name='commodity', on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=25, default=UNDEFINED)
    origin = models.CharField(max_length=20,choices=ORIGIN_CHOICES,default=UNDEFINED)
    usage = models.CharField(verbose_name='Usage', max_length=25, choices=USAGE_CHOICES,default=UNDEFINED)
    size = models.FloatField(verbose_name="Quantity", default=0)
    total_value = models.FloatField(verbose_name="Total Price", default=0)
    total_price = models.FloatField(verbose_name="Total Value", default=0)
    unit_value = models.FloatField(verbose_name="Unit Value", default=1)
    unit_price = models.FloatField(verbose_name="Unit Price", default=1)
    turnover_time = models.FloatField(verbose_name="Turnover Time", default=360)
    demand = models.FloatField(verbose_name="Demand", default=0)
    supply = models.FloatField(verbose_name="Supply", default=0)
    allocation_ratio = models.FloatField(verbose_name="Allocation Ratio", default=1)
    display_order = models.IntegerField(null=True, default=1)
    image_name = models.CharField(max_length=25, default=UNDEFINED)
    tooltip = models.CharField(max_length=50, default=UNDEFINED)
    monetarily_effective_demand=models.FloatField(default=0)
    investment_proportion=models.FloatField(default=0)
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Commodity'
        verbose_name_plural = 'Commodities'

    def comparator_commodity(self):
        comparator_time_stamp=self.simulation.comparator_time_stamp
        comparator_qs=Commodity.objects.filter(
            time_stamp=comparator_time_stamp,
            name=self.name,
            )
        if comparator_qs.count()>1:
            return self
        elif comparator_qs.count()<1:
            return None
        else:
            return comparator_qs.first()

    @property
    def comparator_demand(self):
        return self.comparator_commodity().demand

    @property
    def comparator_supply(self):
        return self.comparator_commodity().supply

    def change_size(self,quantity):
        #! NOTE caller does not have to save TODO is this the best way?
        logger.info(f"Commodity {self.name} is changing its size by {quantity}")
        self.refresh_from_db()
        logger.info(f"Current size:{self.size} value:{self.total_value} price:{self.total_price}")
        new_size=self.size+quantity
        new_price=self.total_price+quantity*self.unit_price
        new_value=self.total_value+quantity*self.unit_value
        if new_size<0 or new_value<0 or new_price<0:
            raise Exception (f"The commodity {self} will become negative with size {new_size}, value {new_value} and price {new_price}")
        self.size=new_size
        self.total_price=new_price
        self.total_value=new_value
        self.save()
        return        

    def current_query_set(self):
        return Commodity.objects.filter(time_stamp=self.user.current_simulation.current_time_stamp)

    def __str__(self):
        return f"[Time Stamp {self.time_stamp}] {self.name}"



