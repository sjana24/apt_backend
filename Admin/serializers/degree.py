from rest_framework import serializers
from ..models import Degree
from .module import ModuleSimpleSerializer, CourseModuleSimpleSerializer

class DegreeSimpleSerializer(serializers.ModelSerializer):
    """
    Simple degree representation used for nesting inside other serializers.
    Prevents circular references and keeps response lightweight.
    """
    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear']

class DegreeSerializer(serializers.ModelSerializer):
    """
    Main degree serializer with nested modules.
    Shows modules inside the degree using ModuleSimpleSerializer.
    """
    modules = ModuleSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'modules']

class DegreeWithModulesSerializer(serializers.ModelSerializer):
    """
    Degree serializer including nested simple modules.
    """
    modules = CourseModuleSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'modules']

class DegreeSearchSerializer(serializers.ModelSerializer):
    """
    Serializer for degree search results.
    """
    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear']

class DegreeModuleSyncSerializer(serializers.ModelSerializer):
    """
    Serializer to handle syncing modules to a degree (PUT/Update).
    Expects a list of module IDs.
    """
    modules_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True,
        required=False
    )

    class Meta:
        model = Degree
        fields = ['id', 'degreeProgram', 'level', 'semester', 'academicYear', 'modules_ids']

    def update(self, instance, validated_data):
        module_ids = validated_data.pop('modules_ids', None)
        instance = super().update(instance, validated_data)
        
        if module_ids is not None:
           
            pass 
        return instance
