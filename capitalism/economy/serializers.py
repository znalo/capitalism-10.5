from rest_framework import serializers
from .models.commodity import (Commodity)

from django.contrib.auth.models import User

class CommoditiesSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # project_name=serializers.PrimaryKeyRelatedField(source='project_FK.description',read_only=True)
    class Meta:
        model=Commodity
        fields=(
          'project_FK',
          'time_stamp_FK',
          'name',
          'origin',
          'usage',
          'unit_value',
          'unit_price',
          'turnover_time',
          'demand',
          'supply',
          'allocation_ratio',
          'owner'
        )

