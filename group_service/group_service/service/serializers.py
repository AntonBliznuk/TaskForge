from rest_framework import serializers 
from . import models


class CreateGroupSerializer(serializers.ModelSerializer):
    """
    Serializer to create a group.
    """
    class Meta:
        model = models.Group
        fields = ['name', 'password', 'description', 'creater_id']


class GroupInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for information about the group.
    """
    class Meta:
        model = models.Group
        fields = ['id', 'name', 'description', 'created_at', 'creater_id']