from . models import Project
from rest_framework import serializers
from users.serializers import UserSerializer

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'admin_id','user']

class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'name', 'description','user']

    