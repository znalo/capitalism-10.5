from enum import auto
from django.db import models
from economy.global_constants import *
from .states import User

class Trace(models.Model):
    time_stamp_id = models.IntegerField(default=0, null=False)
    real_time=models.DateTimeField(auto_now_add=True)
    period = models.IntegerField(default=0, null=False)
    stage = models.CharField(max_length=25, default=UNDEFINED)
    step = models.CharField(max_length=25, default=UNDEFINED)
    project_id = models.IntegerField(default=0, null=False)
    level = models.IntegerField(default=0, null=False)
    message = models.CharField(max_length=250, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    @staticmethod
    def enter(user, level, message):
        try:
            current_time_stamp = user.current_time_stamp
            stamp_number = current_time_stamp.time_stamp
            current_step = current_time_stamp.step
            project_id = current_time_stamp.simulation_FK.project_number
            this_entry = Trace(user=user,time_stamp_id=stamp_number, period=current_time_stamp.period, stage=current_time_stamp.stage, step=current_step, project_id=project_id,level=level, message=(message))
            this_entry.save()
        except Exception as error:
            logger.error(f"Could not make a trace entry because {error}")

    @staticmethod
    def sim_object(value):
        return f"<span class = 'simulation-object'>{value}</span>"

    @staticmethod
    def sim_quantity(value):
        return f"<span class = 'quantity-object'>{value}</span>"