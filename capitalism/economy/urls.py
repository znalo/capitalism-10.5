from django.contrib import admin
from django.conf.urls import url
from economy import views
from economy.actions import control
from django.urls import path, include

urlpatterns = [
    path('', views.landingPage, name='landing-page'),
    path('justlanded/', views.newlyLanded, name='just-landed'),
    path('status/', views.status_update, name='status'),
    path('about-capitalism/', views.about_capitalism, name='about-capitalism'),
    url('^admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    url('tables/report', views.TraceView.as_view(), name='trace'),
    url('tables/economy', views.get_economy_view_context, name='economy'),
    url('tables/time-stamps', views.TimeStampView.as_view(), name='time-stamps'),
    url('tables/industries', views.IndustryView.as_view(), name='industries'),
    url('tables/commodities', views.CommodityView.as_view(), name='commodities'),
    url('tables/social-classes',views.SocialClassView.as_view(), name='social-classes'),
    url('tables/all-owners', views.AllOwnersView.as_view(), name='all-owners'),
    url('tables/simulations', views.SimulationView.as_view(), name='simulations'),
    url('tables/industry-stocks',views.IndustryStockView.as_view(), name='industry-stocks'),
    url('tables/social-stocks', views.SocialStockView.as_view(), name='social-stocks'),
    url('tables/all-stocks', views.AllStocksView.as_view(), name='all-stocks'),

    url('sandbox', views.sandbox, name='sandbox'),
    url('initialize', views.initialize_and_redisplay, name='initialize'),
    url('project-table-rebuild', views.rebuild_project_table, name='project-table-rebuild'),
    url(r'projects/', views.ProjectView.as_view(), name='projects'),
    url(r'stage/(?P<act>[\w-]+)/$', control.stage_execute, name='stage'),
    url(r'control/(?P<period>[\d-]+)/(?P<stage>[\w-]+)/(?P<step>[\w-]+)/$', control.select_comparator, name='comparator-select'),
    url(r'step/(?P<act>[\w-]+)/$', views.step_execute_and_display, name='execute'),
    url(r'disclaimers/', views.disclaimers, name='disclaimers'),
    path('signup/', views.signup, name='signup'),
    url('admin-dashboard', views.AdminDashboard.as_view(), name='admin-dashboard'),
    url('user-dashboard', views.userDashboard, name='user-dashboard'),
    path('userdetail/<int:pk>/', views.UserDetail.as_view(),name='user-detail'),
    path('create-simulation/', views.SimulationCreateView.as_view(), name='create-simulation'),
    path('select-simulation/<int:pk>/', views.simulationSelectView, name='select-simulation'),
    path('delete-simulation/<int:pk>/', views.SimulationDeleteView.as_view(),name='delete-simulation'),
    path('restart-simulation/<int:pk>/', views.simulationRestartView ,name='restart-simulation'),
    path('tracelevel/<int:pk>/', views.TraceLevelSetView.as_view(),name='tracelevel'),
    path('signup/', views.signup, name='signup'),
]

urlpatterns += [
    path('users/', include('django.contrib.auth.urls')),
]

#! We did not use the Matt Freire way of authentication and login which might be better
#     path('login/',LoginView.as_view(),name='login'),
#     path('logout/',LogoutView.as_view(),name='logout'),

#! We used the [Mozilla way](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication)

