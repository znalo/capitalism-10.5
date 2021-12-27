from django.urls import path
from economy import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create a router and register the API viewsets with it.
# This is just a template to show how it works for one of the models
# in case we want to go over to this system
router = DefaultRouter()
router.register(r'commodities', views.CommodityViewSet)
# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]