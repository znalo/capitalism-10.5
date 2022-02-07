from django.db import models
from economy.global_constants import *
from django.contrib.auth.models import AbstractUser
from django.contrib import messages

class User(AbstractUser):
    #! The time_stamp object has a foreign key relation to the user, because there are many stamps in a simulation
    #! However, the User object also needs to know where it is in this simulation.
    #! It therefore has a special field, current_time_stamp, that represents the current state of the simulation
    #! A complication is that we cannot cascade this field. 
    #! This is because, when the data is completely re-initialized, all the timestamps pointing to the user are deleted.
    #! This would include the current_time_stamp. If we cascaded the relation, the user would get deleted.
    #! For the same reason, current_time_stamp allows blank and null (and when deleted, this field is set to null)
    #! TODO there is probably a more foolproof way to deal with this.
    current_time_stamp= models.OneToOneField("TimeStamp", related_name="current_time_stamp", on_delete=models.SET_NULL, blank=True, null=True, default=None)

    @property
    def simulation(self):
        return self.current_time_stamp.simulation_FK

    @property
    def project(self):
        return self.simulation.project_number

    @property
    def current_step(self):
        return self.current_time_stamp.step

    @property
    def current_stage(self):
        return STEPS[self.current_step].stage_name

    def set_project(self,project_number):
        logger.info(f"Changing project of user {self.username} from {self.current_time_stamp.project_number} to {project_number}")
        new_time_stamp=TimeStamp.objects.filter(user=self,project_number=project_number).last() #! pick up wherever the simulation of this project by this user left off
        logger.info(f"The relevant time stamp is {new_time_stamp}")
        self.current_time_stamp=new_time_stamp
        self.save()


    #! Set the comparator of the current time stamp to a new comparator
    def set_current_comparator(self,comparator):
        logger.info(f"User {self} is changing its comparator which is {self.current_time_stamp} from {self.current_time_stamp.current_comparator_time_stamp_FK} to {comparator}")
        self.current_time_stamp.comparator_time_stamp_FK = comparator
        self.current_time_stamp.save()

    #! Move forward one time stamp and clone all the associated objects
    def one_step(self):
        logger.info(f"User {self} is moving time stamp {self.current_time_stamp} forward one step")
        old_time_stamp_id = self.current_time_stamp.id
        new_time_stamp = self.current_time_stamp
        #! create a new timestamp object by saving with pk=None. Forces Django to create a new database object
        new_time_stamp.pk = None
        new_time_stamp.time_stamp += 1
        #! because the new time stamp gets saved to the database, we need to retrieve the old one
        #!TODO there's probably a better way
        old_time_stamp = TimeStamp.objects.get(id=old_time_stamp_id)
        new_time_stamp.save()
        new_time_stamp.comparator_time_stamp_FK = old_time_stamp
        new_time_stamp.save() #! just in case

        #! Next five lines of code are just to report what's going on
        #! Memo:
            #! States are divided into superstates and steps and this affects the logic
            #! The user decides whether they wants to execute a single sub-step, or all the steps in a bunch
            #! We may arrive at this decision either
                # *  because we're only processing stages (user not interested in the detail), or
                # *  because user is halfway through a stage and wants to skip to the next stage
        old_number = new_time_stamp.comparator_time_stamp_FK.time_stamp
        new_number = new_time_stamp.time_stamp
        old_step = new_time_stamp.comparator_time_stamp_FK.step
        new_step = new_time_stamp.step
        logger.info(f"Stepping from Old Time Stamp {old_number} representing step {old_step} to New Time Stamp {new_number} representing step {new_step}")

        #! Now clone all the objects that were associated with the old time stamp, and create identical copies associated with the new stamp
        #! Once that's done, the control logic will invoke the action specified by the new stamp, but that's outside this particular procedure

        #! tell the user she has a new current time stamp, namely the one we just created
        new_time_stamp.clone(old_time_stamp) #! We assume the cloning procedure takes care of saving the new current stamp and all the objects associated with it
        self.current_time_stamp= new_time_stamp
        self.save()

    def __str__(self):
        return self.username

#! Note there is no user field for the projects. They are simply a fixture
#! TODO The admin user, and only the admin user, has the option to re-import projects
class Project(models.Model):
    number = models.IntegerField(null=False, default=1)
    description = models.CharField(max_length=50, default=DEMAND)

    def __str__(self):
        return f"(Project {self.number} {self.description})"

class Simulation(models.Model):
    name=models.CharField(max_length=50,null=False,default = INITIAL)
    project_number = models.IntegerField(default=1) #! We don't have a foreign key to the project because the admin might need to rebuild the project table
    periods_per_year=models.IntegerField(default=1)
    population_growth_rate = models.IntegerField(default=1)
    investment_ratio = models.IntegerField(default=1)
    labour_supply_response = models.CharField(max_length=50, default=UNDEFINED)
    price_response_type = models.CharField(max_length=50, default=UNDEFINED)
    melt_response_type = models.CharField(max_length=50, null=True, blank=True,default=None)
    currency_symbol = models.CharField(max_length=2, default="$")
    quantity_symbol = models.CharField(max_length=2, default="#")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    #! Create a new simulation from the embryo of this simulation object
    #! At this point, we assume that only the bare simulation object exists, and that no time stamps point to it.
    #! Therefore, we have to create all the objects of a simulation, based on the name and project number of this simulation object
    def startup(self):
        try:
            time_stamp=TimeStamp(simulation_FK=self,step=DEMAND,stage='M_C',user=self.user)
            logger.info(f"User {self.user} is creating a new simulation called {self.name} whose project number is {self.project_number}")
            time_stamp.save()
            time_stamp.comparator_time_stamp_FK=time_stamp
            time_stamp.save()
            #! Find the source simulation and clone it to create a new simulation
            #! The 'initialize' action will have created a template for every project
            #! This is uniquely defined by the name "Initial" that the initialize action gives to the template
            #! together with the fact that the time_stamps for all the objects in this simulation will all have the 'time_stamp' field set to 1.
            #! TODO should be less hard-wired
            source_simulation=Simulation.objects.get(name="Initial",project_number=self.project_number,user=self.user)
            logger.info(f"Cloning this simulation from {source_simulation.name} with project number {self.project_number}")
            source_time_stamp=TimeStamp.objects.get(simulation_FK=source_simulation)
            time_stamp.clone(source_time_stamp)
            time_stamp.save()
            self.user.current_time_stamp=time_stamp
            self.user.save()
            return "success"
        except Exception as error:
            logger.error(f"Could not create the requested simulation because {error}")
            return error

    def __str__(self):
        return f"{self.name}.{self.project_number}.{self.user}"

class TimeStamp(models.Model):
    simulation_FK=models.ForeignKey(Simulation, on_delete=models.CASCADE) 
    time_stamp = models.IntegerField(default=1) # ! TODO rename this field to avoid confusion
    step = models.CharField(max_length=50, default=UNDEFINED)
    stage = models.CharField(max_length=50, default=UNDEFINED)
    period = models.IntegerField(default=1)
    comparator_time_stamp_FK = models.ForeignKey("TimeStamp", on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    melt = models.CharField(max_length=50, default=UNDEFINED)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    @property
    def project_number(self):
        return self.simulation_FK.project_number 
    
    def project_FK(self):
        return Project.objects.get(number=self.project_number)
    
    #! create a complete clone of each object from source_time_stamp and assign it to self (which is assumed to be already saved to the database as a new time stamp)
    #! when this is done, pass through the newly-created children linking them to their new parents
    #! (so, for example, connect each stock to its new owner)

    #! First create the clones
    #! cloning method is to set pk=0 and save. See https://django.fun/docs/django-orm-cookbook/en/2.0/copy/
    #! but we must set both .pk and .id to None before it works (see https://www.youtube.com/watch?v=E0oM9r3LhQU)
    #! seems a bit quirky but haven't found another way

    def clone(self, source_time_stamp):
       #! import these here to avoid circular imports
        from .commodity import Commodity
        from .stocks import IndustryStock, SocialStock
        from .owners import Industry, SocialClass

        industries = Industry.objects.filter(time_stamp_FK=source_time_stamp)
        for industry in industries:
            industry.time_stamp_FK = self
            industry.pk = None
            industry.id = None
            industry.save()
            logger.info(f"Created a new Industry record {(industry.name)} with time stamp {industry.time_stamp_FK.time_stamp} which will contain the results of action {industry.time_stamp_FK.step}")

        commodities = Commodity.objects.filter(time_stamp_FK=source_time_stamp)
        for commodity in commodities:
            commodity.pk = None
            commodity.id = None
            commodity.time_stamp_FK = self
            commodity.save()
            logger.info(f"Created a new Commodity record {(commodity.name)} with time stamp {commodity.time_stamp_FK.time_stamp} which will contain the results of action {commodity.time_stamp_FK.step}")

        social_classes = SocialClass.objects.filter(
            time_stamp_FK=source_time_stamp)
        for social_class in social_classes:
            social_class.pk = None
            social_class.id = None
            social_class.time_stamp_FK = self
            social_class.save()
            logger.info(f"Created a new Social Class record {(social_class.name)} with time stamp {social_class.time_stamp_FK.time_stamp} which will contain the results of action {social_class.time_stamp_FK.step}")

        social_stocks = SocialStock.objects.filter(
            time_stamp_FK=source_time_stamp)
        for social_stock in social_stocks:
            social_stock.pk = None
            social_stock.id = None
            social_stock.time_stamp_FK = self
            social_stock.save()
            logger.info(f"Created a new Social Stock record of usage type {(social_stock.usage_type)} for owner {(social_stock.stock_owner_name)} with time stamp {social_stock.time_stamp_FK.time_stamp} which will contain the results of action {social_stock.time_stamp_FK.step}")

        industry_stocks = IndustryStock.objects.filter(
            time_stamp_FK=source_time_stamp)
        for industry_stock in industry_stocks:
            industry_stock.pk = None
            industry_stock.id = None
            industry_stock.time_stamp_FK = self
            industry_stock.save()
            logger.info(f"Created a new Industry Stock record of usage type {(industry_stock.usage_type)} for owner {(industry_stock.stock_owner_name)} with time stamp {industry_stock.time_stamp_FK.time_stamp} which will contain the results of action {industry_stock.time_stamp_FK.step}")

        #! send in the clones
        #! we now connect each new object to the duplicates of its relevant parent objects

    #! connect industries to their related commodities
        logger.info("Connecting cloned records")
        industries = Industry.objects.filter(time_stamp_FK=self)
        for industry in industries:
            commodity_name = industry.commodity_FK.name
            logger.info(f"Connecting Industry {(industry.name)} to its output commodity {(commodity_name)}")
    #! find the commodity with the same name but the new time stamp
            candidates = Commodity.objects.filter(
                name=commodity_name, time_stamp_FK=self)
            if candidates.count() > 1:
                logger.info( f"+++DUPLICATE COMMODITIES {candidates}+++")
            else:
                industry.commodity_FK = candidates.get()
            industry.save()
    #! connect industry stocks to their commodities and owners
        industry_stocks = IndustryStock.objects.filter(
            time_stamp_FK=self)
        for industry_stock in industry_stocks:
            commodity_name = industry_stock.commodity_FK.name
            logger.info(f"Connecting Industry Stock of usage type {(industry_stock.usage_type)} to commodity {(commodity_name)}")
    #! find the commodity that has the same name but the new time stamp
            new_commodity = Commodity.objects.get(
                name=commodity_name, time_stamp_FK=self)
            industry_stock.commodity_FK = new_commodity
    #! find the owner industry
            industry_name = industry_stock.industry_FK.name
            new_industry = Industry.objects.get(
                name=industry_name, time_stamp_FK=self)
            logger.info(f"Connecting Industry Stock of usage type {(industry_stock.usage_type)} to its industry {(industry_name)}")
            industry_stock.industry_FK = new_industry
            industry_stock.stock_owner_FK = new_industry
            industry_stock.save()
            new_industry.save()
    #! connect social stocks to their commodities and owners
        social_stocks = SocialStock.objects.filter(
            time_stamp_FK=self)
        for social_stock in social_stocks:
            commodity_name = social_stock.commodity_FK.name
            logger.info(f"Connecting Social Stock of usage type {(social_stock.usage_type)} to commodity {(commodity_name)}")
    #! find the commodity that has the same name but the new time stamp
            new_commodity = Commodity.objects.get(
                name=commodity_name, time_stamp_FK=self)
            social_stock.commodity_FK = new_commodity
    #! find the owner social class
            social_class_name = social_stock.social_class_FK.name
            new_social_class = SocialClass.objects.get(
                name=social_class_name, time_stamp_FK=self)
            logger.info(f"Connecting Social Stock of usage_type {(social_stock.usage_type)} to its social class {(social_class_name)}")
            social_stock.social_class_FK = new_social_class
            social_stock.stock_owner_FK = new_social_class
            social_stock.save()
            new_social_class.save()

    class Meta:
        ordering = ['time_stamp', ]

    def __str__(self):
        return f"{self.period}.{self.stage}.{self.step}"


