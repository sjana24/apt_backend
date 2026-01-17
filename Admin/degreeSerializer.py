from rest_framework import serializers
from .models import *
from Authenticate.models import UserTable
from .serializer import *

class DegreeSerializer(serializers.ModelSerializer):
    """
    Returns basic degree info without nesting modules.
    Ideal for list views or dropdowns.
    """
    class Meta:
        model = Degree
        fields = [
            'id', 
            'degreeProgram', 
            'level', 
            'semester', 
            'academicYear'
        ]



# 1. THE LINK: CourseStaff -> Staff Name
class StaffAssignmentSerializer(serializers.ModelSerializer):
    staff_name = serializers.ReadOnlyField(source='staff.full_name')
    staff_email = serializers.ReadOnlyField(source='staff.email')

    class Meta:
        model = CourseStaff
        fields = ['id', 'staff', 'staff_name', 'staff_email', 'role']

# 2. THE MODULE: Module -> Linked Staff
class ModuleWithStaffSerializer(serializers.ModelSerializer):
    # This uses the related_name from your CourseStaff model (e.g., 'staff_assignments')
    assigned_staff = StaffAssignmentSerializer(source='staff_assignments', many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = ['id', 'module_name', 'module_code', 'credit', 'assigned_staff']

# 3. THE DEGREE: Degree -> Modules -> Staff
class DegreeDeepSerializer(serializers.ModelSerializer):
    # This uses the related_name from your CourseModule model (e.g., 'modules')
    modules = ModuleWithStaffSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'modules']

class StaffModuleDetailSerializer(serializers.ModelSerializer):
    # Get module details
    module_name = serializers.ReadOnlyField(source='course_module.module_name')
    module_code = serializers.ReadOnlyField(source='course_module.module_code')
    
    # Get the Degree details attached to that module
    degree_details = DegreeSimpleSerializer(source='course_module.degree', read_only=True)

    class Meta:
        model = CourseStaff
        fields = ['id', 'module_name', 'module_code', 'role', 'degree_details', 'assigned_at']



#  update seralizers
class DegreeModuleSyncSerializer(serializers.ModelSerializer):
    # This field accepts a simple list of IDs: [1, 2, 3]
    module_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'module_ids']

    def update(self, instance, validated_data):
        # 1. Extract the module IDs
        module_ids = validated_data.pop('module_ids', None)

        # 2. Update Degree basic info
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 3. If IDs were sent, sync the relationship
        if module_ids is not None:
            # Step A: Disconnect modules that are no longer in this degree
            # (Sets their degree_id to NULL)
            CourseModule.objects.filter(degree=instance).exclude(id__in=module_ids).update(degree=None)

            # Step B: Connect the new list of modules to this degree
            CourseModule.objects.filter(id__in=module_ids).update(degree=instance)

        return instance
    
class DegreeSearchSerializer(serializers.ModelSerializer):
    # This uses the related_name from your CourseModule model (e.g., 'modules')
    # modules = ModuleWithStaffSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram']