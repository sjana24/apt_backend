from rest_framework import serializers
from .models import *
from Authenticate.models import UserTable

class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'created_at']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTable
        # Exclude sensitive fields like password in GET requests
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at']
        read_only_fields = ['role'] # Prevent changing role to 'admin' via this view


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ['id', 'name', 'capacity', 'created_at', 'updated_at']