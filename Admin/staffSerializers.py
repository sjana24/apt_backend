from rest_framework import serializers
from .serializer import *
from .models import *



class CourseStaffMinimalSerializer(serializers.ModelSerializer):
    module_id = serializers.ReadOnlyField(source='course_module.id')
    module_name = serializers.ReadOnlyField(source='course_module.module_name')
    module_code = serializers.ReadOnlyField(source='course_module.module_code')

    class Meta:
        model = CourseStaff
        # Only include the "allowed" values you actually need
        fields = ['id','module_id', 'module_name', 'module_code', 'role']

class StaffSerializer(serializers.ModelSerializer):
    assigned_modules = CourseStaffMinimalSerializer(
        source='module_assignments', 
        many=True, 
        read_only=True
    )
    class Meta:
        model = UserTable
        fields = ['id', 'full_name', 'assigned_modules']


class StaffUpdateSerializer(serializers.ModelSerializer):
    # This shows existing modules for GET requests
    assigned_modules = CourseStaffSerializer(source='module_assignments', many=True, read_only=True)
    
    # This accepts a list of IDs for PUT/PATCH requests [1, 2, 5]
    module_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = UserTable
        fields = ['id', 'email', 'full_name', 'is_active', 'assigned_modules', 'module_ids']

    def update(self, instance, validated_data):
        # 1. Extract module IDs from the request
        module_ids = validated_data.pop('module_ids', None)

        # 2. Update basic fields (name, email, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 3. Handle assignments if module_ids were sent
        if module_ids is not None:
            # Clear previous assignments
            CourseStaff.objects.filter(staff=instance).delete()
            
            # Create new assignments
            new_assignments = [
                CourseStaff(staff=instance, course_module_id=m_id)
                for m_id in module_ids
            ]
            CourseStaff.objects.bulk_create(new_assignments)

        return instance