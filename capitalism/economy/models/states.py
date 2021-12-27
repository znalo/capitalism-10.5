from django.db import models
from django.db.models.base import Model
from django.db.models.fields import IntegerField

from capitalism.global_constants import *

class Log(models.Model):
    time_stamp_id=models.IntegerField(default=0, null=False)
    project_id=models.IntegerField(default=0, null=False)
    level=models.IntegerField(default=0, null=False)
    message=models.CharField(max_length=250,null=False)

    @staticmethod
    def enter(level,message):
        state=State.objects.all()
        if state.count()==0:
            time_stamp_id=0
            project_id=0
        else:
            current_state=State.objects.get()
            time_stamp_id=current_state.time_stamp_FK.time_stamp
            project_id=current_state.time_stamp_FK.project_FK.number

        indent= " "*level
        # print(f"{indent}{message}")
        this_entry=Log(project_id=project_id,time_stamp_id=time_stamp_id,level=level,message=message)
        this_entry.save()

class ControlSuperState(models.Model):
    name=models.CharField(max_length=20,choices=CONTROL_SUPER_STATES,default=UNDEFINED)
    first_substate_name=models.CharField(max_length=20,choices=CONTROL_SUB_STATES,default=UNDEFINED)
    next_superstate_name=models.CharField(max_length=20,choices=CONTROL_SUPER_STATES,default=UNDEFINED)
    owner = models.ForeignKey('auth.User',  on_delete=models.CASCADE, default=1)

class ControlSubState(models.Model):
    name=models.CharField(max_length=20,choices=CONTROL_SUB_STATES)
    super_state_name=models.CharField(max_length=20,choices=CONTROL_SUPER_STATES,default=UNDEFINED)
    next_substate_name=models.CharField(max_length=20,choices=CONTROL_SUB_STATES,default=UNDEFINED)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1)

class Project(models.Model):
    number=models.IntegerField(verbose_name="Project",null=False, default=0)
    description = models.CharField(verbose_name="Project Description", max_length=50, default="###")
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return f"Project {self.number}[{self.description}]"

class TimeStamp(models.Model):
    project_FK = models.ForeignKey(Project, related_name='time_stamp', on_delete=models.CASCADE)
    time_stamp = models.IntegerField(verbose_name="Time Stamp", default=1)
    description = models.CharField(verbose_name="Description", max_length=50, default=UNDEFINED)
    period = models.IntegerField(verbose_name="Period", default=1)
    super_state_FK = models.ForeignKey(ControlSuperState, max_length=20, on_delete=models.CASCADE, default=1)
    sub_state_FK = models.ForeignKey(ControlSubState, max_length=20, on_delete=models.CASCADE, default=1)
    comparator_time_stamp_ID = models.IntegerField(verbose_name="Comparator", default=1)
    melt = models.CharField(verbose_name="MELT", max_length=50, default=UNDEFINED)
    population_growth_rate = models.IntegerField(verbose_name="Population Growth Rate", default=1)
    investment_ratio = models.IntegerField(verbose_name="Investment Ratio", default=1)
    labour_supply_response = models.CharField(verbose_name="Labour Supply Response", max_length=50, default=UNDEFINED)
    price_response_type = models.CharField(verbose_name="Price Response Type", max_length=50, default=UNDEFINED)
    melt_response_type = models.CharField(verbose_name="MELT Response Type", max_length=50, null=True)
    currency_symbol = models.CharField(verbose_name="Currency Symbol", max_length=2, default="$")
    quantity_symbol = models.CharField(verbose_name="Quantity Symbol", max_length=2, default="#")
    owner = models.ForeignKey('auth.User', related_name='timestamps', on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = 'Time Stamp'
        verbose_name_plural = 'Time Stamps'
        ordering=['project_FK__number','time_stamp',]

    def __str__(self):
        return f"[Time {self.time_stamp}] [Project {self.project_FK.number}] {self.description}"

class State(models.Model):
    name = models.CharField(primary_key=True, default="Initial", max_length=50)
    time_stamp_FK = models.OneToOneField(TimeStamp, related_name='state', on_delete=models.CASCADE, default=1)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.name

