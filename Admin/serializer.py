from rest_framework import serializers
from .models import *
from Authenticate.models import UserTable

# 1. Simple Degree Serializer (Used inside Module GET results)
class DegreeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear']

# 2. Simple Module Serializer (Used inside Degree GET results)
class ModuleSimpleSerializer(serializers.ModelSerializer):
    degree_details = DegreeSimpleSerializer(source='degree', read_only=True)
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'created_at','degree','degree_details']

# 3. Main Degree Serializer (GET /degrees/)
class DegreeSerializer(serializers.ModelSerializer):
    # Shows modules inside the degree, but uses the simple version
    modules = ModuleSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'modules']

class CourseStaffSerializer(serializers.ModelSerializer):
    # For GET requests: show readable names
    staff_name = serializers.ReadOnlyField(source='staff.full_name')
    module_name = serializers.ReadOnlyField(source='course_module.module_name')
    
    # For POST requests: use the IDs
    staff = serializers.PrimaryKeyRelatedField(queryset=UserTable.objects.all())
    course_module = serializers.PrimaryKeyRelatedField(queryset=CourseModule.objects.all())

    class Meta:
        model = CourseStaff
        fields = ['id', 'staff', 'staff_name', 'course_module', 'module_name', 'role', 'assigned_at']

# 4. Main Course Module Serializer (GET /modules/)
class CourseModuleSerializer(serializers.ModelSerializer):
    # NOW WE USE THE SIMPLE DEGREE SERIALIZER HERE
    # This prevents the "modules inside degree inside module" problem
    degree_details = DegreeSimpleSerializer(source='degree', read_only=True) 
    degree = serializers.PrimaryKeyRelatedField(queryset=Degree.objects.all())

    assigned_staff = CourseStaffSerializer(source='staff_assignments', many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'degree', 'degree_details', 'created_at']

# --- Other Serializers Stay the Same ---
class StaffSerializer(serializers.ModelSerializer):
    assigned_modules = CourseStaffSerializer(source='module_assignments', many=True, read_only=True)
    class Meta:
        model = UserTable
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at','assigned_modules']
        read_only_fields = ['role']

class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ['id', 'name', 'capacity', 'created_at', 'updated_at']

class CourseModuleSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit']

# Serializer for the Degree including its nested modules
class DegreeWithModulesSerializer(serializers.ModelSerializer):
    # 'modules' is the related_name defined in the CourseModule model ForeignKey
    modules = CourseModuleSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'modules']
