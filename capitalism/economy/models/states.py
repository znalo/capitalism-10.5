from django.db import models
from economy.global_constants import *
from .users import User



class Project(models.Model):
    number = models.IntegerField(null=False, default=1)
    description = models.CharField(max_length=50, default=DEMAND)

    def __str__(self):
        return f"Project {self.number}[{self.description}]"


class TimeStamp(models.Model):
    project_FK = models.ForeignKey(Project, related_name='time_stamp', on_delete=models.CASCADE, null=True,blank=True,default=None)
    #! TODO we've allowed blank and null because of the problem of first-time initialization. A better solution is possible
    time_stamp = models.IntegerField(default=1) # ! TODO rename this field to avoid confusion
    step = models.CharField(max_length=50, default=UNDEFINED)
    stage = models.CharField(max_length=50, default=UNDEFINED)
    period = models.IntegerField(default=1)
    comparator_time_stamp_FK = models.ForeignKey("TimeStamp", on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    melt = models.CharField(max_length=50, default=UNDEFINED)
    population_growth_rate = models.IntegerField(default=1)
    investment_ratio = models.IntegerField(default=1)
    labour_supply_response = models.CharField(max_length=50, default=UNDEFINED)
    price_response_type = models.CharField(max_length=50, default=UNDEFINED)
    melt_response_type = models.CharField(max_length=50, null=True, blank=True,default=None)
    currency_symbol = models.CharField(max_length=2, default="$")
    quantity_symbol = models.CharField(max_length=2, default="#")

    class Meta:
        ordering = ['project_FK__number', 'time_stamp', ]

    def __str__(self):
        return f"[Time {self.time_stamp}(id:{self.id}) description: {self.step}] [Project {self.project_FK.number}] "


class State(models.Model):
    name = models.CharField(primary_key=True, default="Initial", max_length=50)
    time_stamp_FK = models.OneToOneField(
        TimeStamp, related_name='state', on_delete=models.CASCADE, blank=True, null=True, default=None)
    #! TODO we've allowed blank and null because of the problem of first-time initialization. A better solution is possible

#! minimal function to create a barebones consistent database
#! let everything default except period
    def failsafe_restart():
        Project.objects.all().delete()
        TimeStamp.objects.all().delete()
        State.objects.all().delete()
        first_project=Project(number=1,description=DEMAND)
        first_project.save()
        first_stamp=TimeStamp(
            time_stamp=1,
            project_FK=first_project,
            period=0,
            )
        first_stamp.save()
        failsafe_state=State(name="Failsafe Temporary",time_stamp_FK=first_stamp)
        failsafe_state.save()

    @staticmethod
    def current_state():
        try:
            return State.objects.get()
        except:
            State.failsafe_restart()

    @staticmethod
    def current_stamp():
        return State.current_state().time_stamp_FK

    @staticmethod
    def current_project():
        return State.current_state().time_stamp_FK.project_FK

    @staticmethod
    def step():
        return State.current_stamp().step

    @staticmethod
    def stage():
        return STEPS[State.step()].stage_name

    # TODO the user should also be a selector for the state, since different users will have different states
    @staticmethod
    def set_project(time_stamp):
        Log.debug_entry(
            0, f"Setting project to {time_stamp.project_FK.description}")
        try:
            current_state = State.current_state()
            current_state.time_stamp_FK = time_stamp
            current_state.save()
        except:
            raise Exception(
                f"Project or its time stamp either does not exist or is corrupt. This could be a data error, but it might be a programme error. Cannot continue, sorry")

    @staticmethod
    def create_stamp():
        Log.enter(0, "MOVING ONE TIME STAMP FORWARD")
        current_state = State.current_state()
        current_time_stamp = State.current_stamp()
        this_project = current_time_stamp.project_FK
        old_time_stamp = TimeStamp.objects.filter(
            project_FK=this_project).order_by('time_stamp').last()
        remember_where_we_parked = old_time_stamp.id
        new_time_stamp = old_time_stamp
        #! create a new timestamp object by saving with pk=None. Forces Django to create a new database object
        new_time_stamp.pk = None
        new_time_stamp.time_stamp += 1
        remembered_time_stamp = TimeStamp.objects.get(
            id=remember_where_we_parked)
        new_time_stamp.save()
        new_time_stamp.comparator_time_stamp_FK = remembered_time_stamp
        new_time_stamp.save()
        #! reset the current state
        current_state.time_stamp_FK = new_time_stamp
        current_state.save()
        old_number = new_time_stamp.comparator_time_stamp_FK.time_stamp
        new_number = new_time_stamp.time_stamp
        old_step = new_time_stamp.comparator_time_stamp_FK.step
        new_step = new_time_stamp.step
        Log.debug_entry(
            2, f"Stepping from Old Time Stamp {old_number} representing step {old_step} to New Time Stamp {new_number} representing step {new_step}")
        return new_time_stamp

    #! Set the comparator of the current time stamp to a new comparator

    @staticmethod
    def set_current_comparator(comparator):
        current_time_stamp = State.current_stamp()
        current_time_stamp.comparator_time_stamp_FK = comparator
        current_time_stamp.save()

    #! create a complete clone of each object and set it to point to the new time stamp
    #! when this is done, pass through the newly-created children linking them to their new parents
    #! cloning method is to set pk=0 and save. See https://django.fun/docs/django-orm-cookbook/en/2.0/copy/
    #! but we must set both .pk and .id to None before it works (see https://www.youtube.com/watch?v=E0oM9r3LhQU)
    #! seems a bit quirky but haven't found another way
    @staticmethod
    def clone(old_time_stamp, new_time_stamp):
       #! import these here to avoid circular imports
        from .commodity import Commodity
        from .stocks import IndustryStock, SocialStock
        from .owners import Industry, SocialClass

        industries = Industry.objects.filter(time_stamp_FK=old_time_stamp)
        for industry in industries:
            industry.time_stamp_FK = new_time_stamp
            industry.pk = None
            industry.id = None
            industry.save()
            Log.debug_entry(
                2, f"Created a new Industry record {Log.sim_object(industry.name)} with time stamp {industry.time_stamp_FK.time_stamp} which will contain the results of action {industry.time_stamp_FK.step}")

        commodities = Commodity.objects.filter(time_stamp_FK=old_time_stamp)
        for commodity in commodities:
            commodity.pk = None
            commodity.id = None
            commodity.time_stamp_FK = new_time_stamp
            commodity.save()
            Log.debug_entry(
                2, f"Created a new Commodity record {Log.sim_object(commodity.name)} with time stamp {commodity.time_stamp_FK.time_stamp} which will contain the results of action {commodity.time_stamp_FK.step}")

        social_classes = SocialClass.objects.filter(
            time_stamp_FK=old_time_stamp)
        for social_class in social_classes:
            social_class.pk = None
            social_class.id = None
            social_class.time_stamp_FK = new_time_stamp
            social_class.save()
            Log.debug_entry(
                2, f"Created a new Social Class record {Log.sim_object(social_class.name)} with time stamp {social_class.time_stamp_FK.time_stamp} which will contain the results of action {social_class.time_stamp_FK.step}")

        social_stocks = SocialStock.objects.filter(
            time_stamp_FK=old_time_stamp)
        for social_stock in social_stocks:
            social_stock.pk = None
            social_stock.id = None
            social_stock.time_stamp_FK = new_time_stamp
            social_stock.save()
            Log.debug_entry(
                2, f"Created a new Social Stock record of usage type {Log.sim_object(social_stock.usage_type)} for owner {Log.sim_object(social_stock.stock_owner_name)} with time stamp {social_stock.time_stamp_FK.time_stamp} which will contain the results of action {social_stock.time_stamp_FK.step}")

        industry_stocks = IndustryStock.objects.filter(
            time_stamp_FK=old_time_stamp)
        for industry_stock in industry_stocks:
            industry_stock.pk = None
            industry_stock.id = None
            industry_stock.time_stamp_FK = new_time_stamp
            industry_stock.save()
            Log.debug_entry(
                2, f"Created a new Industry Stock record of usage type {Log.sim_object(industry_stock.usage_type)} for owner {Log.sim_object(industry_stock.stock_owner_name)} with time stamp {industry_stock.time_stamp_FK.time_stamp} which will contain the results of action {industry_stock.time_stamp_FK.step}")
        return

    #! this method works with create_stamp (and should perhaps be integrated into it)
    #! when a new stamp is created (by 'move_one_stamp'), it first creates the stamp and then clones every object
    #! so that the time_stamp and the objects together constitute a new 'state' of the simulation
    #! Therefore, once the new objects have been created, all their foreign keys must be linked to their correct parents
    @staticmethod
    def connect_stamp(new_time_stamp):
        #! import these here to avoid circular imports
        from .commodity import Commodity
        from .stocks import IndustryStock, SocialStock
        from .owners import Industry, SocialClass

        #! connect industries to their related commodities
        Log.debug_entry(1, "Connecting records")
        industries = Industry.objects.filter(time_stamp_FK=new_time_stamp)
        for industry in industries:
            commodity_name = industry.commodity_FK.name
            Log.debug_entry(
                2, f"Connecting Industry {Log.sim_object(industry.name)} to its output commodity {Log.sim_object(commodity_name)}")
    #! find the commodity with the same name but the new time stamp
            candidates = Commodity.objects.filter(
                name=commodity_name, time_stamp_FK=new_time_stamp)
            if candidates.count() > 1:
                Log.debug_entry(0, f"+++DUPLICATE COMMODITIES {candidates}+++")
            else:
                industry.commodity_FK = candidates.get()
            industry.save()
    #! connect industry stocks to their commodities and owners
        industry_stocks = IndustryStock.objects.filter(
            time_stamp_FK=new_time_stamp)
        for industry_stock in industry_stocks:
            commodity_name = industry_stock.commodity_FK.name
            Log.debug_entry(
                2, f"Connecting Industry Stock of usage type {Log.sim_object(industry_stock.usage_type)} to commodity {Log.sim_object(commodity_name)}")
    #! find the commodity that has the same name but the new time stamp
            new_commodity = Commodity.objects.get(
                name=commodity_name, time_stamp_FK=new_time_stamp)
            industry_stock.commodity_FK = new_commodity
    #! find the owner industry
            industry_name = industry_stock.industry_FK.name
            new_industry = Industry.objects.get(
                name=industry_name, time_stamp_FK=new_time_stamp)
            Log.debug_entry(
                2, f"Connecting Industry Stock of usage type {Log.sim_object(industry_stock.usage_type)} to its industry {Log.sim_object(industry_name)}")
            industry_stock.industry_FK = new_industry
            industry_stock.stock_owner_FK = new_industry
            industry_stock.save()
            new_industry.save()
    #! connect social stocks to their commodities and owners
        social_stocks = SocialStock.objects.filter(
            time_stamp_FK=new_time_stamp)
        for social_stock in social_stocks:
            commodity_name = social_stock.commodity_FK.name
            Log.debug_entry(
                2, f"Connecting Social Stock of usage type {Log.sim_object(social_stock.usage_type)} to commodity {Log.sim_object(commodity_name)}")
    #! find the commodity that has the same name but the new time stamp
            new_commodity = Commodity.objects.get(
                name=commodity_name, time_stamp_FK=new_time_stamp)
            social_stock.commodity_FK = new_commodity
    #! find the owner social class
            social_class_name = social_stock.social_class_FK.name
            new_social_class = SocialClass.objects.get(
                name=social_class_name, time_stamp_FK=new_time_stamp)
            Log.debug_entry(
                2, f"Connecting Social Stock of usage_type {Log.sim_object(social_stock.usage_type)} to its social class {Log.sim_object(social_class_name)}")
            social_stock.social_class_FK = new_social_class
            social_stock.stock_owner_FK = new_social_class
            social_stock.save()
            new_social_class.save()

    #! Create a new state by moving forward one time stamp (see 'move_one_stamp')
    #! States are divided into superstates and steps and this affects the logic
    #! The user decides whether they wants to execute a single sub-step, or all the steps in a bunch
    #! We may arrive at this decision either
    # *  because we're only processing stages (user not interested in the detail), or
    # *  because user is halfway through a stage and wants to skip to the next stage
    @staticmethod
    def one_step():
        #! The State 'knows' the time_stamp
        old_time_stamp = State.current_stamp()
        new_time_stamp = State.create_stamp()
        State.clone(old_time_stamp, new_time_stamp)
        State.connect_stamp(new_time_stamp)
        # ! probably redundant - the time_stamp should be remembered in new_time_stamp
        time_stamp = State.current_stamp()
        time_stamp.save()
        #! The receiver will perform the action specified by step

    def __str__(self):
        return self.name

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

    def debug_entry(level, message):
        if Log.logging_mode == "verbose":
            Log.enter(level, message)

    @staticmethod
    def sim_object(value):
        return f"<span class = 'simulation-object'>{value}</span>"

    @staticmethod
    def sim_quantity(value):
        return f"<span class = 'quantity-object'>{value}</span>"