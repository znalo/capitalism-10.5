from django.contrib import admin
from .models.states import Log, Project, TimeStamp, ControlSuperState,ControlSubState
from .models.commodity import Commodity
from .models.owners import StockOwner, Industry, SocialClass
from .models.stocks import SocialStock, State, IndustryStock
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class CommodityResource(resources.ModelResource):
   class Meta:
      model = Commodity
 
class CommodityAdmin(ImportExportModelAdmin):
   resource_class = CommodityResource

class ProjectResource(resources.ModelResource):
   class Meta:
      model = Project
 
class ProjectAdmin(ImportExportModelAdmin):
   resource_class = ProjectResource

class TimeStampResource(resources.ModelResource):
   class Meta:
      model = TimeStamp
 
class TimeStampAdmin(ImportExportModelAdmin):
   resource_class = TimeStampResource   

class IndustryResource(resources.ModelResource):
   class Meta:
      model = Industry
 
class IndustryAdmin(ImportExportModelAdmin):
   resource_class = IndustryResource   
   
class SocialClassResource(resources.ModelResource):
   class Meta:
      model = SocialClass
 
class SocialClassAdmin(ImportExportModelAdmin):
   resource_class = SocialClassResource   

class SocialStockResource(resources.ModelResource):
   class Meta:
      model = SocialStock
 
class SocialStockAdmin(ImportExportModelAdmin):
   resource_class = SocialStockResource   
      
class IndustryStockResource(resources.ModelResource):
   class Meta:
      model = IndustryStock
 
class IndustryStockAdmin(ImportExportModelAdmin):
   resource_class = IndustryStockResource   

class StateResource(resources.ModelResource):
   class Meta:
      model = State
 
class StateAdmin(ImportExportModelAdmin):
   resource_class = StateResource   

class LogResource(resources.ModelResource):
   class Meta:
      model=Log

class LogAdmin(ImportExportModelAdmin):
   resource_class=LogResource

class ControlSuperStateResource(resources.ModelResource):
   class Meta:
      model=ControlSuperState

class ControlSubStateResource(resources.ModelResource):
   class Meta:
      model=ControlSubState

class ControlSuperStateAdmin(ImportExportModelAdmin):
   resource_class=ControlSuperState

class ControlSubStateAdmin(ImportExportModelAdmin):
   resource_class=ControlSubState

admin.site.register(Commodity,CommodityAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(TimeStamp,TimeStampAdmin)
admin.site.register(Industry,IndustryAdmin)
admin.site.register(SocialClass,SocialClassAdmin)
admin.site.register(SocialStock,SocialStockAdmin)
admin.site.register(IndustryStock,IndustryStockAdmin)
admin.site.register(State,StateAdmin)
admin.site.register(Log,LogAdmin)
admin.site.register(ControlSuperState,ControlSuperStateAdmin)
admin.site.register(ControlSubState,ControlSubStateAdmin)
