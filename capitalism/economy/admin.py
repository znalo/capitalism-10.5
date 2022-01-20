from django.contrib import admin
from .models.states import Log, Project, TimeStamp
from .models.commodity import Commodity
from .models.owners import Industry, SocialClass
from .models.stocks import SocialStock, State, IndustryStock

admin.site.register(Commodity)
admin.site.register(Project)
admin.site.register(TimeStamp)
admin.site.register(Industry)
admin.site.register(SocialClass)
admin.site.register(SocialStock)
admin.site.register(IndustryStock)
admin.site.register(State)
admin.site.register(Log)
