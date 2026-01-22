from rest_framework import serializers
from .models import *
# from Authenticate.models import UserTable


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ['id', 'name', 'capacity','availability', 'created_at', 'updated_at']

# labAvailabilitySerializer.py
from rest_framework import serializers
from datetime import datetime, time
import re
from .models import Lab, TimetableSlot, Degree, CourseModule
from .labSerializer import LabSerializer

class LabAvailabilityRequestSerializer(serializers.Serializer):
    """Serializer for lab availability request"""
    date = serializers.DateField(required=True)
    time_range = serializers.CharField(required=True)
    degree_id = serializers.IntegerField(required=False, allow_null=True)
    module_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_time_range(self, value):
        """Validate and normalize time range format"""
        # Remove any quotes
        value = str(value).strip().strip('"\'').strip()
        
        # Try different time range formats
        formats_to_try = [
            # With spaces around dash
            r'^(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$',
            # Without spaces
            r'^(\d{1,2}:\d{2})-(\d{1,2}:\d{2})$',
            # With "to"
            r'^(\d{1,2}:\d{2})\s+to\s+(\d{1,2}:\d{2})$',
            # With en dash
            r'^(\d{1,2}:\d{2})\s*–\s*(\d{1,2}:\d{2})$',
        ]
        
        for pattern in formats_to_try:
            match = re.match(pattern, value, re.IGNORECASE)
            if match:
                start_str, end_str = match.groups()
                try:
                    # Parse times
                    start_time = datetime.strptime(start_str, '%H:%M').time()
                    end_time = datetime.strptime(end_str, '%H:%M').time()
                    
                    if start_time >= end_time:
                        raise serializers.ValidationError("Start time must be before end time")
                    
                    # Return normalized format (HH:MM - HH:MM)
                    return f"{start_str} - {end_str}"
                except ValueError:
                    continue
        
        raise serializers.ValidationError(
            "Time range must be in format 'HH:MM-HH:MM' or 'HH:MM - HH:MM'"
        )
    
    def validate(self, data):
        """Additional validation"""
        # Validate degree exists if provided
        degree_id = data.get('degree_id')
        if degree_id:
            try:
                degree = Degree.objects.get(id=degree_id)
                data['degree'] = degree
            except Degree.DoesNotExist:
                raise serializers.ValidationError({
                    'degree_id': f"Degree with ID {degree_id} does not exist"
                })
        
        # Validate module exists if provided
        module_id = data.get('module_id')
        if module_id:
            try:
                module = CourseModule.objects.get(id=module_id)
                data['module'] = module
            except CourseModule.DoesNotExist:
                raise serializers.ValidationError({
                    'module_id': f"Module with ID {module_id} does not exist"
                })
        
        return data

class AvailableLabSerializer(LabSerializer):
    """Extended Lab serializer with availability and conflict details"""
    is_available = serializers.BooleanField(read_only=True)
    conflict_details = serializers.SerializerMethodField()
    
    class Meta(LabSerializer.Meta):
        fields = LabSerializer.Meta.fields + ['is_available', 'conflict_details']
    
    def get_conflict_details(self, obj):
        """Get conflict details if lab is occupied"""
        request = self.context.get('request')
        if request and hasattr(request, 'query_params'):
            date_str = request.query_params.get('date')
            time_range = request.query_params.get('time_range')
            
            if date_str and time_range:
                try:
                    # Check if this lab is already booked at this time
                    from datetime import datetime
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    # Check for existing booking in TimetableSlot
                    existing_booking = TimetableSlot.objects.filter(
                        lab=obj,
                        slot_date=date,
                        time_range=time_range
                    ).first()
                    
                    if existing_booking:
                        return {
                            'id': existing_booking.id,
                            'degree': {
                                'id': existing_booking.degree.id,
                                'name': existing_booking.degree.degreeProgram
                            } if existing_booking.degree else None,
                            'module': {
                                'id': existing_booking.module.id if existing_booking.module else None,
                                'name': existing_booking.module.module_name if existing_booking.module else None,
                                'code': existing_booking.module.module_code if existing_booking.module else None
                            },
                            'time_range': existing_booking.time_range,
                            'note': existing_booking.note,
                            'created_by': existing_booking.created_by.full_name if existing_booking.created_by else None
                        }
                except (ValueError, AttributeError):
                    pass
        return None