from django.contrib import admin
from django.conf.urls import url
from rest_framework import routers
from economy import views
from economy.actions import control
from django.urls import path, include
from economy.actions.control import select_project
from economy.actions.initialize import initialize

router = routers.DefaultRouter()
router.register(r'api-commodities', views.CommodityViewSet)

urlpatterns = [
    path('', views.landingPage, name='landing-page'),
    url('^admin/', admin.site.urls),
    url('^api/', include(router.urls)),
    path('api/tables/', include('economy.urls')),
    url('api/commodities', views.commodityTable, name='api-commodities'),
    url('api/views', views.apiViews, name='api-views'),

    url('log/collapsible', views.log_collapsible, name='log-collapsible'),
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
    url(r'super/(?P<act>[\w-]+)/$', control.super_step_execute, name='stage'),
    url(r'control/(?P<state>[\w-]+)/(?P<step>[\w-]+)/$', control.comparator_select, name='comparator-select'),
    url(r'sub/(?P<act>[\w-]+)/$', control.sub_step_execute, name='execute'),

]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
