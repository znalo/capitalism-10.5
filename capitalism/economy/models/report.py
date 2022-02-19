from enum import auto
from django.db import models
from economy.global_constants import *
from .states import User, Simulation

class Trace(models.Model):
    time_stamp_id = models.IntegerField(default=0, null=False)
    simulation=models.ForeignKey(Simulation, on_delete=models.CASCADE, null=True, blank=True, default=None)
    real_time=models.DateTimeField(auto_now_add=True)
    period = models.IntegerField(default=0, null=False)
    stage = models.CharField(max_length=25, default=UNDEFINED)
    step = models.CharField(max_length=25, default=UNDEFINED)
    project_id = models.IntegerField(default=0, null=False)
    level = models.IntegerField(default=0, null=False)
    message = models.CharField(max_length=250, null=False)

    @staticmethod
    def enter(simulation, level, message): 
        try:
            current_time_stamp = simulation.current_time_stamp
            current_step = current_time_stamp.step
            project_id = simulation.project_number
            this_entry = Trace(simulation=simulation, period=current_time_stamp.period, stage=current_time_stamp.stage, step=current_step, project_id=project_id,level=level, message=(message))
            this_entry.save()
        except Exception as error:
            logger.error(f"Could not make a trace entry because {error}, for message {message}")

    @staticmethod
    def o(value):
        return f"<span class = 'simulation-object'>{value}</span>"

    @staticmethod
    def q(value):
        return f"<span class = 'quantity-object'>{value}</span>"