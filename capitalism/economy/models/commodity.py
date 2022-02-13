from django.db import models
from .states import TimeStamp, Simulation
from ..global_constants import ORIGIN_CHOICES, USAGE_CHOICES, UNDEFINED, logger
from .report import Trace

class Commodity(models.Model):
    time_stamp_FK = models.ForeignKey(TimeStamp, related_name='commodity', on_delete=models.CASCADE)
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
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, null=True, default=None)

    class Meta:
        verbose_name = 'Commodity'
        verbose_name_plural = 'Commodities'
        ordering = ['time_stamp_FK']

    def comparator_commodity(self):
        comparator_time_stamp=self.time_stamp_FK.comparator_time_stamp_FK
        comparator_qs=Commodity.objects.filter(
            time_stamp_FK=comparator_time_stamp,
            name=self.name,
            )
        if comparator_qs.count()>1:
            return self
        elif comparator_qs.count()<1:
            return None
        else:
            return comparator_qs.first()

    def set_commodity_size(self):
        simulation=self.simulation
        current_time_stamp=simulation.current_time_stamp
        from .stocks import Stock #! have to do this here to avoid circular import. TODO not very happy with this
        Trace.enter(simulation,1,f"Recaculating the size of commodity {self.name}; currently this is {self.size} ")
        stocks=Stock.objects.filter(commodity_FK=self,time_stamp_FK=current_time_stamp) 
        #! TODO What a mess
        #! TODO can we resolve this mess by converting all related querysets into methods of the relevant objects
        size=0
        for stock in stocks:
            size+=stock.size
        self.size=size
        self.save()
        Trace.enter(simulation,2,f"Commodity {Trace.sim_object(self.name)} size is {Trace.sim_quantity(size)} ")

    @property
    def comparator_demand(self):
        return self.comparator_commodity().demand

    @property
    def comparator_supply(self):
        return self.comparator_commodity().supply

    @staticmethod
    def set_commodity_sizes(user):
        simulation=user.simulation
        Trace.enter(simulation,1,f"Recalculating all commodity sizes for user {user}")
        logger.info(f"Recalculating all commodity sizes for user {user}")
        commodities=Commodity.objects.filter(time_stamp_FK=user.current_simulation.current_time_stamp)
        for commodity in commodities:
            commodity.set_commodity_size()

    def current_query_set(self):
        return Commodity.objects.filter(time_stamp_FK=self.user.current_simulation.current_time_stamp)

    def __str__(self):
        return f"[Time Stamp {self.time_stamp_FK.time_stamp}] {self.name}"



