from django.contrib import admin
from django.conf.urls import url
from rest_framework import routers
from economy import views
from economy.actions import control, exchange, produce, distribution
from django.urls import path, include

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

    url('tables/economy', views.EconomyView.as_view(), name='economy'),
    url('tables/time-stamps', views.TimeStampView.as_view(), name='time-stamps'),
    url('tables/industries', views.IndustryView.as_view(), name='industries'),
    url('tables/commodities', views.CommodityView.as_view(), name='commodities'),
    url('tables/social-classes', views.SocialClassView.as_view(), name='social-classes'),
    url('tables/all-owners', views.AllOwnersView.as_view(), name='all-owners'),
    url('tables/industry-stocks', views.IndustryStockView.as_view(), name='industry-stocks'),
    url('tables/social-stocks', views.SocialStockView.as_view(), name='social-stocks'),
    url('tables/all-stocks', views.AllStocksView.as_view(), name='all-stocks'),

    url('exchange/demand', exchange.calculate_demand, name='calculate-demand'),
    url('exchange/supply', exchange.calculate_supply, name='calculate-supply'),
    url('exchange/allocate', exchange.allocate_supply, name='allocate'),
    url('exchange/trade', exchange.trade, name='trade'),

    url('control/sandbox', views.sandbox, name='sandbox'),
    url('control/move-one-stamp', control.move_one_stamp, name='move-one-stamp'),
    url('control/initialize', control.initialize, name='initialize'),

    url('production/produce', produce.produce_all, name='produce'),
    url('production/prices', produce.prices, name='prices'),
    url('production/reproduce', produce.reproduce, name='reproduce'),

    url('distribution/revenue', distribution.revenue,name='revenue'),
    url('distribution/accumulate', distribution.revenue,name='accumulate'),

]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]

