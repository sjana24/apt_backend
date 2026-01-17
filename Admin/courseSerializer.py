from rest_framework import serializers
from .models import *
from Authenticate.models import UserTable
from .serializer import *

# create
class CreateModuleSerializer(serializers.ModelSerializer):
    # degree_details = DegreeSimpleSerializer(source='degree', read_only=True)
    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit']

# get
class ModuleSimpleSerializer(serializers.ModelSerializer):
    # Get degree details (Existing)
    degree_details = DegreeSimpleSerializer(source='degree', read_only=True)
    
    # Get staff details (New)
    # This uses the CourseStaffSerializer to show who is teaching this module
    assigned_staff = CourseStaffSerializer(source='staff_assignments', many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = ['id', 
            'module_name', 
            'module_code', 
            'credit', 
            'created_at', 
            'degree', 
            'degree_details',
            'assigned_staff'  
        ]

#  Edit
class ModuleUpdateSerializer(serializers.ModelSerializer):
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
                    defaults={'role': 'Lecturer'} # Default role if creating new
                )

        return instance
    
#  get single staff courses 
class ModuleWithDegreeSerializer(serializers.ModelSerializer):
    degree_details = DegreeSimpleSerializer(source='degree', read_only=True)

    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'degree_details']

class StaffAssignmentDetailSerializer(serializers.ModelSerializer):
    # This nests the module (and its degree) inside the assignment
    module_details = ModuleWithDegreeSerializer(source='course_module', read_only=True)

    class Meta:
        model = CourseStaff
        fields = ['id', 'role', 'assigned_at', 'module_details']