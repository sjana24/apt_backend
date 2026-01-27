from rest_framework import serializers
from ..models import Lab

class LabSerializer(serializers.ModelSerializer):
    """
    Serializer for laboratory spaces.
    """
    class Meta:
        model = Lab
        fields = ['id', 'name', 'lab_code', 'capacity', 'availability', 'created_at', 'updated_at']
