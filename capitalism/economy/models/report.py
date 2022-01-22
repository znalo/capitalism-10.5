from django.db import models
from economy.global_constants import *
from .users import User
from .states import State

class Log(models.Model):
    time_stamp_id = models.IntegerField(default=0, null=False)
    period = models.IntegerField(default=0, null=False)
    stage = models.CharField(max_length=25, default=UNDEFINED)
    step = models.CharField(max_length=25, default=UNDEFINED)
    project_id = models.IntegerField(default=0, null=False)
    level = models.IntegerField(default=0, null=False)
    message = models.CharField(max_length=250, null=False)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    logging_mode = "verbose"

    @staticmethod
    def enter(level, message):
        if (State.objects.all().count())!=0:
            time_stamp = State.current_stamp()
            stamp_number = time_stamp.time_stamp
            current_step = time_stamp.step
            project_id = time_stamp.project_FK.number
            this_entry = Log(time_stamp_id=stamp_number, period=time_stamp.period, stage=time_stamp.stage, step=current_step, project_id=project_id,level=level, message=(message))
            this_entry.save()
        else:
            this_entry=Log(time_stamp_id=0, period=0, stage="Not yet started", step="Not yet started", project_id=0,level=level, message=(message))

    @staticmethod
    def sim_object(value):
        return f"<span class = 'simulation-object'>{value}</span>"

    @staticmethod
    def sim_quantity(value):
        return f"<span class = 'quantity-object'>{value}</span>"