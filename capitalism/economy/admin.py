from django.contrib import admin
from .models.states import Project, TimeStamp, User, Simulation
from .models.report import Trace
from .models.commodity import Commodity
from .models.owners import Industry, SocialClass
from .models.stocks import SocialStock, IndustryStock

admin.site.register(Commodity)
admin.site.register(Project)
admin.site.register(TimeStamp)
admin.site.register(Industry)
admin.site.register(SocialClass)
admin.site.register(SocialStock)
admin.site.register(IndustryStock)
admin.site.register(Trace)
admin.site.register(User)
admin.site.register(Simulation)
