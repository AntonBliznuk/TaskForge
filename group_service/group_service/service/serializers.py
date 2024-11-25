from rest_framework import serializers 
from . import models


class CreateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ['name', 'password', 'description', 'creater_id']


class GroupInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ['id', 'name', 'description', 'created_at', 'creater_id']