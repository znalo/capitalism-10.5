import django_filters
from .models.owners import Industry

class IndustryFilter(django_filters.FilterSet):
    model=Industry
    fields=('industry_name', 'commodity_name', 'output', 'growth_rate' )
