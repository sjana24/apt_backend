from rest_framework import serializers
from .models import UserTable

class UserTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTable
        # Specify exactly which fields to send to React
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at']
        # Ensure password is never sent back to the frontend
        extra_kwargs = {
            'password': {'write_only': True}
        }