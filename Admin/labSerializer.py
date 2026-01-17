from rest_framework import serializers
from .models import *
# from Authenticate.models import UserTable


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ['id', 'name', 'capacity','availability', 'created_at', 'updated_at']