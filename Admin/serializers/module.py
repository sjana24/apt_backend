from rest_framework import serializers
from ..models import CourseModule, Degree
# Circular import handling needed for degree details?
# We can use 'DegreeSimpleSerializer' logic here or import inside method if strict cycle.
# For now, let's redefine a minimal degree serializer locally or handle imports carefully.

class DegreeSimpleForResult(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear']

class ModuleSimpleSerializer(serializers.ModelSerializer):
    """
    Simple module representation with nested degree details.
    Used inside Degree GET results.
    """
    degree_details = DegreeSimpleForResult(source='degree', read_only=True)
    
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'created_at', 'degree', 'degree_details']

from .staff import CourseStaffSerializer

class CourseModuleSerializer(serializers.ModelSerializer):
    """
    Main course module serializer with degree and staff details.
    """
    degree_details = DegreeSimpleForResult(source='degree', read_only=True)
    degree = serializers.PrimaryKeyRelatedField(queryset=Degree.objects.all())
    assigned_staff = CourseStaffSerializer(source='staff_assignments', many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'degree', 'degree_details', 'created_at', 'assigned_staff']

class CourseModuleSimpleSerializer(serializers.ModelSerializer):
    """
    Lightweight module representation for nested usage.
    """
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit']
