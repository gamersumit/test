from . models import Project, Logs, ScreenCaptures
from rest_framework import serializers
from admins.serializers import UserSerializer

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'admin_id','users']

class ProjectSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'name', 'description','users']

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = ['id', 'project_id', 'user_id', 'date', 'start_time', 'end_time', 'description', 'images']

class ScreenCaptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenCaptures
        fields = ['id', 'log_id', 'image']