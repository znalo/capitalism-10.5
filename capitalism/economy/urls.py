from django.contrib import admin
from django.conf.urls import url
from economy import views
from economy.actions import control
from django.urls import path, include
from economy.actions.control import select_project

urlpatterns = [
    path('', views.landingPage, name='landing-page'),
    url('^admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # new
    url('report/table', views.TraceView.as_view(), name='trace'),

    url('tables/economy', views.get_economy_view_context, name='economy'),
    url('tables/time-stamps', views.TimeStampView.as_view(), name='time-stamps'),
    url('tables/industries', views.IndustryView.as_view(), name='industries'),
    url('tables/commodities', views.CommodityView.as_view(), name='commodities'),
    url('tables/social-classes',
        views.SocialClassView.as_view(), name='social-classes'),
    url('tables/all-owners', views.AllOwnersView.as_view(), name='all-owners'),
    url('tables/industry-stocks',
        views.IndustryStockView.as_view(), name='industry-stocks'),
    url('tables/social-stocks', views.SocialStockView.as_view(), name='social-stocks'),
    url('tables/all-stocks', views.AllStocksView.as_view(), name='all-stocks'),

    url('sandbox', views.sandbox, name='sandbox'),
    url('initialize', views.initialize_and_redisplay, name='initialize'),
    url(r'projects/', views.ProjectView.as_view(), name='projects'),
    url(r'project/(?P<project_number>[\d-]+)', select_project, name='project-select'),
    url(r'stage/(?P<act>[\w-]+)/$', control.stage_execute, name='stage'),
    url(r'control/(?P<period>[\d-]+)/(?P<stage>[\w-]+)/(?P<step>[\w-]+)/$', control.comparator_select, name='comparator-select'),
    url(r'step/(?P<act>[\w-]+)/$', control.step_execute, name='execute'),
    url(r'disclaimers/', views.disclaimers, name='disclaimers'),

# #! The Matt Freire way of authentication and login
#     path('login/',LoginView.as_view(),name='login'),
#     path('logout/',LogoutView.as_view(),name='logout'),
    path('signup/', views.signup, name='signup'),
]
#! The [Mozilla way](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication)
#! See also https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
#! NOTE we ran into problems server-side because custom user model was created mid-project.
#! See https://code.djangoproject.com/ticket/25313

urlpatterns += [
    path('users/', include('django.contrib.auth.urls')),
]
