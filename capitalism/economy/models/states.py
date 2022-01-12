from django.db import models
from django.db.models.base import Model
from capitalism.global_constants import *
from django.utils.safestring import mark_safe
from django.utils.html import escape

class Log(models.Model):
    time_stamp_id=models.IntegerField(default=0, null=False)
    substate=models.CharField(max_length=25,default=UNDEFINED)
    project_id=models.IntegerField(default=0, null=False)
    level=models.IntegerField(default=0, null=False)
    message=models.CharField(max_length=250,null=False)

    logging_mode="verbose"

    @staticmethod
    def enter(level,message):
        try:
            time_stamp=State.current_stamp()
            stamp_number=time_stamp.time_stamp #! TODO rename this field to avoid confusion
            current_substate=time_stamp.description        
            project_id=time_stamp.project_FK.number
        except:
            project_id = 1
            stamp_number=1
            current_substate="corrupt" #! TODO figure out how to ensure the project doesn't start in a corrupt state (which happens because the State table doesn't contain anything)
        this_entry=Log(project_id=project_id,time_stamp_id=stamp_number,substate=current_substate,level=level,message=(message))
        this_entry.save()

    def debug_entry(level,message):
        if Log.logging_mode=="verbose":
            Log.enter(level,message)

    @staticmethod
    def sim_object(value):
        return f"<span class = 'simulation-object'>{value}</span>"

    @staticmethod
    def sim_quantity(value):
        return f"<span class = 'quantity-object'>{value}</span>"

class Project(models.Model):
    number=models.IntegerField(null=False, default=0)
    description = models.CharField(max_length=50, default="###")
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"Project {self.number}[{self.description}]"

class TimeStamp(models.Model):
    project_FK = models.ForeignKey(Project, related_name='time_stamp', on_delete=models.CASCADE)
    time_stamp = models.IntegerField(default=1)
    description = models.CharField(max_length=50, default=UNDEFINED)
    period = models.IntegerField(default=1)
    comparator_time_stamp_FK = models.ForeignKey("TimeStamp", on_delete=models.DO_NOTHING, null=True)
    melt = models.CharField(max_length=50, default=UNDEFINED)
    population_growth_rate = models.IntegerField(default=1)
    investment_ratio = models.IntegerField(default=1)
    labour_supply_response = models.CharField(max_length=50, default=UNDEFINED)
    price_response_type = models.CharField(max_length=50, default=UNDEFINED)
    melt_response_type = models.CharField(max_length=50, null=True)
    currency_symbol = models.CharField(max_length=2, default="$")
    quantity_symbol = models.CharField(max_length=2, default="#")
    owner = models.ForeignKey('auth.User', related_name='timestamps', on_delete=models.CASCADE, default=1)

    class Meta:
         ordering=['project_FK__number','time_stamp',]

    def __str__(self):
        return f"[Time {self.time_stamp}(id:{self.id}) description: {self.description}] [Project {self.project_FK.number}] "

class State(models.Model):
    name = models.CharField(primary_key=True, default="Initial", max_length=50)
    time_stamp_FK = models.OneToOneField(TimeStamp, related_name='state', on_delete=models.CASCADE, default=1)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1)

    @staticmethod
    def current_state():
        try:
            return State.objects.get()
        except:
            raise Exception ("Corrupted State object: cannot continue. This is most likely a data error. Try re-initialising using loaddata")

    @staticmethod
    def current_stamp():
        return State.current_state().time_stamp_FK

    @staticmethod
    def substate():
        return State.current_stamp().description

    @staticmethod
    def superstate():
        return SUBSTATES[State.substate()].superstate_name

    #TODO the user should also be a selector for the state, since different users will have different states
    @staticmethod
    def set_project(time_stamp):
        Log.debug_entry(0,f"Setting project to {time_stamp.project_FK.description}")
        try:
            current_state=State.current_state()
            current_state.time_stamp_FK=time_stamp
            current_state.save()
        except:
            raise Exception (f"Project or its time stamp either does not exist or is corrupt. This could be a data error, but it might be a programme error. Cannot continue, sorry")


    def __str__(self):
        return self.name

    @staticmethod
    def create_stamp():
        Log.enter(1, "MOVING ONE TIME STAMP FORWARD")
        current_state = State.current_state()
        current_time_stamp = State.current_stamp()
        this_project = current_time_stamp.project_FK
        old_time_stamp = TimeStamp.objects.filter(
            project_FK=this_project).order_by('time_stamp').last()
        remember_where_we_parked=old_time_stamp.id
        new_time_stamp = old_time_stamp
        #! create a new timestamp object by saving with pk=None. Forces Django to create a new database object
        new_time_stamp.pk = None
        new_time_stamp.time_stamp += 1
        # new_time_stamp.description = "Temporary"#! TODO this should be set to the current action
        remembered_time_stamp=TimeStamp.objects.get(id=remember_where_we_parked)
        new_time_stamp.save()
        new_time_stamp.comparator_time_stamp_FK=remembered_time_stamp
        new_time_stamp.save()
        #! reset the current state
        current_state.time_stamp_FK = new_time_stamp
        current_state.save()
        Log.debug_entry(
            2, f"Stepping from Old Time Stamp {new_time_stamp.comparator_time_stamp_FK.time_stamp} to New Time Stamp {new_time_stamp.time_stamp}")
        return new_time_stamp

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
                2, f"Created a new Industry record {Log.sim_object(industry.name)} with time stamp {industry.time_stamp_FK.time_stamp}")

        commodities = Commodity.objects.filter(time_stamp_FK=old_time_stamp)
        for commodity in commodities:
            commodity.pk = None
            commodity.id = None
            commodity.time_stamp_FK = new_time_stamp
            commodity.save()
            Log.debug_entry(
                2, f"Created a new Commodity record {Log.sim_object(commodity.name)} with time stamp {commodity.time_stamp_FK.time_stamp}")

        social_classes = SocialClass.objects.filter(time_stamp_FK=old_time_stamp)
        for social_class in social_classes:
            social_class.pk = None
            social_class.id = None
            social_class.time_stamp_FK = new_time_stamp
            social_class.save()
            Log.debug_entry(
                2, f"Created a new Social Class record {Log.sim_object(social_class.name)} with time stamp {social_class.time_stamp_FK.time_stamp}")

        social_stocks = SocialStock.objects.filter(time_stamp_FK=old_time_stamp)
        for social_stock in social_stocks:
            social_stock.pk = None
            social_stock.id = None
            social_stock.time_stamp_FK = new_time_stamp
            social_stock.save()
            Log.debug_entry(
                2, f"Created a new Social Stock record of usage type {Log.sim_object(social_stock.usage_type)} for owner {Log.sim_object(social_stock.stock_owner_name)} with time stamp {social_stock.time_stamp_FK.time_stamp}")

        industry_stocks = IndustryStock.objects.filter(
            time_stamp_FK=old_time_stamp)
        for industry_stock in industry_stocks:
            industry_stock.pk = None
            industry_stock.id = None
            industry_stock.time_stamp_FK = new_time_stamp
            industry_stock.save()
            Log.debug_entry(
                2, f"Created a new Industry Stock record of usage type {Log.sim_object(industry_stock.usage_type)} for owner {Log.sim_object(industry_stock.stock_owner_name)} with time stamp {industry_stock.time_stamp_FK.time_stamp}")
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
            industry_stock.stock_owner_FK= new_industry
            industry_stock.save()
            new_industry.save()
    #! connect social stocks to their commodities and owners
        social_stocks = SocialStock.objects.filter(time_stamp_FK=new_time_stamp)
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
            social_stock.stock_owner_FK= new_social_class
            social_stock.save()
            new_social_class.save()

    #! Create a new state by moving forward one time stamp (see 'move_one_stamp')
    #! States are divided into superstates and substates and this affects the logic
    #! The user decides whether they wants to execute a single sub-step, or all the steps in a bunch
    #! We may arrive at this decision either 
    #*  because we're only processing superstates (user not interested in the detail), or
    #*  because user is halfway through a superstate and wants to skip to the next superstate
    @staticmethod
    def substep():
        #! The State 'knows' the time_stamp 
        old_time_stamp = State.current_stamp()
        new_time_stamp = State.create_stamp()
        State.clone(old_time_stamp, new_time_stamp)
        State.connect_stamp(new_time_stamp)
        time_stamp=State.current_stamp() #! probably redundant - the time_stamp should be remembered in new_time_stamp
        time_stamp.save()
        #! The receiver will perform the action specified by substate
