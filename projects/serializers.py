from . models import Project, Logs, ScreenCaptures, KeyMousePress
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

class LogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = ['id', 'project_id', 'user_id','start_timestamp','end_timestamp', 'description']

class LogEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = ['start_timestamp','end_timestamp', 'description']


class ScreenCaptureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenCaptures
        fields = ['id','log_id', 'image','created_at']

class KeyMousePressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyMousePress
        fields = ['id','log_id', 'keyboardPress','mouseClick','created_at']
        
class LogSerializer(serializers.ModelSerializer):
    images = ScreenCaptureCreateSerializer(many=True, read_only=True)
    key_and_mouse_press=KeyMousePressCreateSerializer(many=True, read_only=True)
    class Meta:
        model = Logs
        fields = ['id', 'project_id', 'user_id','start_timestamp','end_timestamp', 'description', 'images','key_and_mouse_press']

class UserProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description']


class LogInstanceCreateSerializer(serializers.ModelSerializer):
    images = ScreenCaptureCreateSerializer(many=True, read_only=True)
    key_and_mouse_press=KeyMousePressCreateSerializer(many=True, read_only=True)
    class Meta:
        model = Logs
        fields = ['id', 'project_id', 'user_id','start_timestamp','end_timestamp', 'description', 'images','key_and_mouse_press']
    