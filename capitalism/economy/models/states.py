from django.db import models
from economy.global_constants import *
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

"""
NOTE: The time_stamp object has a foreign key relation to the user, because there are many stamps in a simulation.
However, the User object also needs to know which simulation it is currently connected to.
It therefore has a special field, current_simulation, that represents the simulation. We cannot cascade this field. 
This is because, when the data is completely re-initialized, all the simulations owned by this user are deleted whether or not they are current (via the user attribute of the Simulation object) This would include the current simulation
"""
class User(AbstractUser):
    current_simulation=models.OneToOneField("Simulation", related_name="simulation_user", on_delete=models.SET_NULL,blank=True, null=True, default=None) 

    @property
    def simulation(self):
        return self.current_simulation

    @property
    def project(self):
        return self.simulation.project_number

    @property
    def current_step(self):
        return self.simulation.current_time_stamp.step

    @property
    def current_stage(self):
        return STEPS[self.current_step].stage_name

    def set_current_comparator(self,comparator):
        logger.info(f"User {self} is changing its comparator which is {self.current_time_stamp} from {self.simulation.current_comparator_time_stamp} to {comparator}")
        self.simulation.comparator_time_stamp = comparator
        self.current_time_stamp.save()

    def __str__(self):
        return self.username

class Project(models.Model):
#! Note there is no user field for the projects. They are simply a fixture
    number = models.IntegerField(null=False, default=1)
    description = models.CharField(max_length=50, default=DEMAND)

    def __str__(self):
        return f"(Project {self.number} {self.description})"

class Simulation(models.Model):
    name=models.CharField(max_length=50,null=False,default = UNDEFINED)
    current_time_stamp= models.OneToOneField("TimeStamp", related_name="current_time_stamp",on_delete=models.SET_NULL, blank=True, null=True, default=None)
    comparator_time_stamp=models.OneToOneField("TimeStamp", related_name="comparator_time_stamp",on_delete=models.SET_NULL, blank=True, null=True, default=None)
    project_number = models.SmallIntegerField(default=1) #! We don't have a foreign key to the project because the admin might need to rebuild the project table
    trace_display_level=models.IntegerField(default=5)
    periods_per_year=models.SmallIntegerField(default=1)
    population_growth_rate = models.FloatField(default=1)
    investment_ratio = models.FloatField(default=1)
    labour_supply_response = models.CharField(max_length=50, default=UNDEFINED)
    price_response_type = models.CharField(max_length=50, default=UNDEFINED)
    melt_response_type = models.CharField(max_length=50, null=True, blank=True,default=None)
    currency_symbol = models.CharField(max_length=2, default="$")
    quantity_symbol = models.CharField(max_length=2, default="#")
    melt=models.FloatField(null=False, blank=False,default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    @property
    def initial_capital(self):
        return self.current_time_stamp.initial_capital

    @property
    def current_capital(self):
        return self.current_time_stamp.current_capital

    @property
    def profit(self):
        return self.current_time_stamp.profit

    @property
    def profit_rate(self):
        return self.current_time_stamp.profit_rate

    @property
    def comparator_initial_capital(self):
        return self.comparator_time_stamp.initial_capital

    @property
    def comparator_current_capital(self):
        return self.comparator_time_stamp.current_capital

    @property
    def comparator_profit(self):
        return self.comparator_time_stamp.profit

    @property
    def comparator_profit_rate(self):
        return self.comparator_time_stamp.profit_rate

    @property
    def project_description(self):
        return Project.objects.get(number=self.project_number).description

    def startup(self):
    #! Create a new simulation from the embryo of this simulation object, which was created by SimulationCreateView.
    #! We now have to create all the objects of this simulation, based on its name.
        try:
            logger.info(f"User {self.user} is populating the simulation {self.name} which has project number {self.project_number}")
            #! First create my current_time_stamp (as a prelude to cloning it)
            time_stamp=TimeStamp(simulation=self,step=DEMAND,stage='M_C',user=self.user)
            time_stamp.save()
            self.current_time_stamp=time_stamp
            self.comparator_time_stamp=time_stamp
            self.save()
            #! Find the source simulation and clone it to create a new simulation
            source_simulation=Simulation.objects.get(name="Initial",project_number=self.project_number,user=self.user)
            logger.info(f"Cloning this simulation from {source_simulation.name} with project number {self.project_number}")
            source_time_stamp=source_simulation.current_time_stamp
            time_stamp.clone(source_time_stamp)
            time_stamp.save() # TODO is this necessary? 'clone' should save it.
            self.current_time_stamp=time_stamp
            self.save()
            self.user.current_simulation=self #! Necessary because my user will not yet know that I am its new simulation
            self.user.save()
            return "success"
        except Exception as error:
            logger.error(f"Could not create the requested simulation because {error}")
            return error

    def one_step(self):
    #! Move forward one time stamp and clone all the associated objects
        logger.info(f"User {self.user} of simulation {self} intends to move time stamp {self.current_time_stamp} forward one step")
        old_id = self.current_time_stamp.id
        new_time_stamp = self.current_time_stamp
        new_time_stamp.pk = None
        new_time_stamp.save()
        old_time_stamp = TimeStamp.objects.get(id=old_id) #! TODO is there a better way?
    #! Now clone all the objects that were associated with the old time stamp, and create identical copies associated with the new stamp
        new_time_stamp.clone(old_time_stamp)
        logger.info(f"Stepping from Time Stamp with id {old_time_stamp.id}({old_time_stamp.step}) to new time stamp {new_time_stamp.id} ({new_time_stamp.step})")
        self.current_time_stamp=new_time_stamp
        self.comparator_time_stamp=old_time_stamp
        self.save()

    def __str__(self):
        return f"{self.name}.{self.user}[{self.id}]"

class TimeStamp(models.Model):
    simulation=models.ForeignKey(Simulation, on_delete=models.CASCADE) 
    step = models.CharField(max_length=50, default=UNDEFINED)
    stage = models.CharField(max_length=50, default=UNDEFINED)
    period = models.IntegerField(default=1)
    melt=models.FloatField(null=False, blank=False,default=1) 
    #! By setting negative defaults on the following fields, I hope programming errors will be easier to spot
    total_value=models.FloatField(null=False, blank=False,default=-1)
    total_price=models.FloatField(null=False, blank=False,default=-1)
    initial_capital=models.FloatField(null=False, blank=False,default=-1)
    current_capital=models.FloatField(null=False, blank=False,default=1)
    profit=models.FloatField(null=False, blank=False,default=-1)
    profit_rate=models.FloatField(null=False, blank=False,default=-1)

    @property
    def project_number(self):
        return self.simulation.project_number 
 
    def clone(self, source_time_stamp):
    #! create a complete clone of each object from source_time_stamp and assign it to self 
    #! (which is assumed to be already saved to the database as a new time stamp)
    #! when this is done, pass through the newly-created children linking them to their new parents
    #! (so, for example, connect each stock to its new owner)

    #! Cloning method is to set pk=0 and save. See https://django.fun/docs/django-orm-cookbook/en/2.0/copy/
    #! but we must set both .pk and .id to None before it works (see https://www.youtube.com/watch?v=E0oM9r3LhQU)
    #! seems a bit quirky but haven't found another way
    #! import these here to avoid circular imports
        from .commodity import Commodity
        from .stocks import IndustryStock, SocialStock
        from .owners import Industry, SocialClass

        industries = Industry.objects.filter(time_stamp=source_time_stamp)
        for industry in industries:
            industry.time_stamp = self
            industry.pk = None
            industry.id = None
            industry.save()
            logger.info(f"Created a new Industry record {(industry.name)} with time stamp {industry.time_stamp} which will contain the results of action {industry.time_stamp.step}")

        commodities = Commodity.objects.filter(time_stamp=source_time_stamp)
        for commodity in commodities:
            commodity.pk = None
            commodity.id = None
            commodity.time_stamp = self
            commodity.save()
            logger.info(f"Created a new Commodity record {(commodity.name)} with time stamp {commodity.time_stamp} which will contain the results of action {commodity.time_stamp.step}")

        social_classes = SocialClass.objects.filter(
            time_stamp=source_time_stamp)
        for social_class in social_classes:
            social_class.pk = None
            social_class.id = None
            social_class.time_stamp = self
            social_class.save()
            logger.info(f"Created a new Social Class record {(social_class.name)} with time stamp {social_class.time_stamp} which will contain the results of action {social_class.time_stamp.step}")

        social_stocks = SocialStock.objects.filter(
            time_stamp=source_time_stamp)
        for social_stock in social_stocks:
            social_stock.pk = None
            social_stock.id = None
            social_stock.time_stamp = self
            social_stock.save()
            logger.info(f"Created a new Social Stock record of usage type {(social_stock.usage_type)} for owner {(social_stock.stock_owner.name)} with time stamp {social_stock.time_stamp} which will contain the results of action {social_stock.time_stamp.step}")

        industry_stocks = IndustryStock.objects.filter(
            time_stamp=source_time_stamp)
        for industry_stock in industry_stocks:
            industry_stock.pk = None
            industry_stock.id = None
            industry_stock.time_stamp = self
            industry_stock.save()
            logger.info(f"Created a new Industry Stock record of usage type {(industry_stock.usage_type)} for owner {(industry_stock.stock_owner.name)} with time stamp {industry_stock.time_stamp} which will contain the results of action {industry_stock.time_stamp.step}")

        #! send in the clones
        #! we now connect each new object to the duplicates of its relevant parent objects

    #! connect industries to their related commodities
        logger.info("Connecting cloned records")
        industries = Industry.objects.filter(time_stamp=self)
        for industry in industries:
            commodity_name = industry.commodity.name
            logger.info(f"Connecting Industry {(industry.name)} to its output commodity {(commodity_name)}")
    #! find the commodity with the same name but the new time stamp
            candidates = Commodity.objects.filter(
                name=commodity_name, time_stamp=self)
            if candidates.count() > 1:
                logger.info( f"+++DUPLICATE COMMODITIES {candidates}+++")
            else:
                industry.commodity = candidates.get()
            industry.save()
    #! connect industry stocks to their commodities and owners
        industry_stocks = IndustryStock.objects.filter(
            time_stamp=self)
        for industry_stock in industry_stocks:
            commodity_name = industry_stock.commodity.name
            logger.info(f"Connecting Industry Stock of usage type {(industry_stock.usage_type)} to commodity {(commodity_name)}")
    #! find the commodity that has the same name but the new time stamp
            new_commodity = Commodity.objects.get(
                name=commodity_name, time_stamp=self)
            industry_stock.commodity = new_commodity
    #! find the owner industry
            industry_name = industry_stock.industry.name
            new_industry = Industry.objects.get(
                name=industry_name, time_stamp=self)
            logger.info(f"Connecting Industry Stock of usage type {(industry_stock.usage_type)} to its industry {(industry_name)}")
            industry_stock.industry = new_industry
            industry_stock.stock_owner = new_industry
            industry_stock.save()
            new_industry.save()
    #! connect social stocks to their commodities and owners
        social_stocks = SocialStock.objects.filter(
            time_stamp=self)
        for social_stock in social_stocks:
            commodity_name = social_stock.commodity.name
            logger.info(f"Connecting Social Stock with id {social_stock.id} of usage type {(social_stock.usage_type)} to commodity {(commodity_name)}")
    #! find the commodity that has the same name but the new time stamp
            new_commodity = Commodity.objects.get(
                name=commodity_name, time_stamp=self)
            social_stock.commodity = new_commodity
    #! find the owner social class
            social_class_name = social_stock.social_class.name
            new_social_class = SocialClass.objects.get(
                name=social_class_name, time_stamp=self)
            logger.info(f"Connecting Social Stock with id {social_stock.id} of usage_type {(social_stock.usage_type)} to social class {(social_class_name)}")
            social_stock.social_class = new_social_class
            social_stock.stock_owner = new_social_class
            social_stock.save()
            new_social_class.save()

        return

    def __str__(self):
        return f"{self.simulation.project_number}|{self.period}.{self.stage}.{self.step}[{self.id}]"


