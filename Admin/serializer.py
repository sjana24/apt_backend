from rest_framework import serializers
from .models import *
from Authenticate.models import UserTable


# === SIMPLE/NESTED SERIALIZERS ===

class DegreeSimpleSerializer(serializers.ModelSerializer):
    """
    Simple degree representation used for nesting inside other serializers.
    Prevents circular references and keeps response lightweight.
    """
    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear'] #only these will exposed to the response when sending it back to the frontend


class ModuleSimpleSerializer(serializers.ModelSerializer):
    """
    Simple module representation with nested degree details.
    Used inside Degree GET results.
    """
    degree_details = DegreeSimpleSerializer(source='degree', read_only=True)
    
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'created_at', 'degree', 'degree_details']


# === MAIN SERIALIZERS ===

class DegreeSerializer(serializers.ModelSerializer):
    """
    Main degree serializer with nested modules.
    Shows modules inside the degree using ModuleSimpleSerializer.
    """
    modules = ModuleSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'modules']


class CourseStaffSerializer(serializers.ModelSerializer):
    """
    Bidirectional serializer for staff-course assignments.
    GET: Shows readable staff name and module name
    POST: Accepts staff and course_module IDs
    """
    # For GET requests: show readable names
    staff_name = serializers.ReadOnlyField(source='staff.full_name')
    module_name = serializers.ReadOnlyField(source='course_module.module_name')
    
    # For POST requests: use the IDs
    staff = serializers.PrimaryKeyRelatedField(queryset=UserTable.objects.all())
    course_module = serializers.PrimaryKeyRelatedField(queryset=CourseModule.objects.all())

    class Meta:
        model = CourseStaff
        fields = ['id', 'staff', 'staff_name', 'course_module', 'module_name', 'role', 'assigned_at']


class CourseModuleSerializer(serializers.ModelSerializer):
    """
    Main course module serializer with degree and staff details.
    """
    degree_details = DegreeSimpleSerializer(source='degree', read_only=True)
    degree = serializers.PrimaryKeyRelatedField(queryset=Degree.objects.all())
    assigned_staff = CourseStaffSerializer(source='staff_assignments', many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'degree', 'degree_details', 'created_at', 'assigned_staff']


class StaffSerializer(serializers.ModelSerializer):
    """
    Main staff serializer with assigned modules.
    """
    assigned_modules = CourseStaffSerializer(source='module_assignments', many=True, read_only=True)
    
    class Meta:
        model = UserTable
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at', 'assigned_modules']
        read_only_fields = ['role']


class LabSerializer(serializers.ModelSerializer):
    """
    Serializer for laboratory spaces.
    """
    class Meta:
        model = Lab
        fields = ['id', 'name', 'capacity', 'created_at', 'updated_at']


class CourseModuleSimpleSerializer(serializers.ModelSerializer):
    """
    Lightweight module representation for nested usage.
    """
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit']


class DegreeWithModulesSerializer(serializers.ModelSerializer):
    """
    Degree serializer including nested simple modules.
    """
    modules = CourseModuleSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'modules']
