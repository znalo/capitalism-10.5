from django.contrib import admin
from django.conf.urls import url
from economy import views
from economy.actions import control
from django.urls import path
from economy.actions.control import select_project
from economy.actions.initialize import initialize

urlpatterns = [
    path('', views.landingPage, name='landing-page'),
    url('^admin/', admin.site.urls),

    url('log/table', views.LogView.as_view(), name='log'),
    url('log/mode', views.switch_log_mode, name='mode'),

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

    url('control/sandbox', views.sandbox, name='sandbox'),
    url('control/initialize', initialize, name='initialize'),
    url(r'project/(?P<id>[\d-]+)', select_project, name='project-select'),
    url(r'stage/(?P<act>[\w-]+)/$', control.stage_execute, name='stage'),
    url(r'control/(?P<period>[\d-]+)/(?P<stage>[\w-]+)/(?P<step>[\w-]+)/$', control.comparator_select, name='comparator-select'),
    url(r'step/(?P<act>[\w-]+)/$', control.step_execute, name='execute'),

]

