from rest_framework import serializers
from ..models import CourseStaff, CourseModule
from Authenticate.models import UserTable

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


class StaffSerializer(serializers.ModelSerializer):
    """
    Main staff serializer with assigned modules.
    """
    assigned_modules = CourseStaffSerializer(source='module_assignments', many=True, read_only=True)
    
    class Meta:
        model = UserTable
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at', 'assigned_modules']
        read_only_fields = ['role']

from ..models import CourseStaff, CourseModule, Degree

class DegreeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear']

class ModuleInfoSerializer(serializers.ModelSerializer):
    degree_details = DegreeInfoSerializer(source='degree', read_only=True)
    
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'degree', 'degree_details']

class StaffModuleDetailSerializer(serializers.ModelSerializer):
    module_details = ModuleInfoSerializer(source='course_module', read_only=True)
    staff_name = serializers.ReadOnlyField(source='staff.full_name')
    
    class Meta:
        model = CourseStaff
        fields = ['id', 'role', 'module_details', 'assigned_at', 'staff_name']
