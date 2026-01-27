from rest_framework import serializers
from ..models import *
from Authenticate.models import UserTable
from ..serializer import *


# === COURSE MODULE SERIALIZERS ===

class CreateModuleSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for creating new course modules.
    Only accepts essential fields: name, code, and credit.
    """
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit']


class ModuleSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying course modules with related data.
    Includes degree details and assigned staff for each module.
    """
    degree_details = DegreeSimpleSerializer(source='degree', read_only=True)
    assigned_staff = CourseStaffSerializer(source='staff_assignments', many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = [
            'id', 
            'module_name', 
            'module_code', 
            'credit', 
            'created_at', 
            'degree', 
            'degree_details',
            'assigned_staff'  
        ]


class ModuleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating course modules.
    Handles updating module details and syncing staff assignments.
    """
    # Field to accept a list of Staff IDs: [5, 8]
    staff_id = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    # Field to accept a Degree ID
    degree = serializers.PrimaryKeyRelatedField(queryset=Degree.objects.all(), required=False)

    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'degree', 'staff_id']

    def update(self, instance, validated_data):
        # 1. Extract the staff IDs
        staff_ids = validated_data.pop('staff_id', None)

        # 2. Update basic fields and Degree FK
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 3. Sync Staff Assignments if staff_ids provided
        if staff_ids is not None:
            # Remove current staff not in the new list
            CourseStaff.objects.filter(course_module=instance).exclude(staff_id__in=staff_ids).delete()
            
            # Add new staff assignments
            for s_id in staff_ids:
                # get_or_create prevents errors if the staff is already assigned
                CourseStaff.objects.get_or_create(
                    course_module=instance, 
                    staff_id=s_id,
                    defaults={'role': 'Lecturer'}  # Default role if creating new
                )

        return instance


# === COURSE-STAFF RELATIONSHIP SERIALIZERS ===

class ModuleWithDegreeSerializer(serializers.ModelSerializer):
    """
    Lightweight module serializer showing degree association.
    Used within staff assignment details.
    """
    degree_details = DegreeSimpleSerializer(source='degree', read_only=True)

    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'degree_details']


class StaffAssignmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for staff course assignments.
    Nests module and degree information for each assignment.
    """
    module_details = ModuleWithDegreeSerializer(source='course_module', read_only=True)
    staff_id = serializers.IntegerField(source='staff.id', read_only=True)
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)

    class Meta:
        model = CourseStaff
        fields = ['id', 'role', 'assigned_at', 'module_details', 'staff_id', 'staff_name']