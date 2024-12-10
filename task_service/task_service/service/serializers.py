from rest_framework import serializers 
from . import models

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ['id', 'group_id', 'title', 'discription', 'photo', 'status', 'user_id']