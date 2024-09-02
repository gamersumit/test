from . models import Admin
from rest_framework import serializers

class AdminCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'first_name', 'last_name', 'email', 'password']

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'first_name', 'last_name', 'email']

class GoogleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['code']

