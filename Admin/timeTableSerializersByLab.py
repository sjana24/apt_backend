# serializers/lab_timetable_serializer.py
from rest_framework import serializers
from datetime import datetime, timedelta
from django.db.models import Q
from Admin.models import Lab, TimetableSlot

# Define lab time slots (adjust as needed)
LAB_TIME_SLOTS = [
    "08:00 - 09:00",
    "09:00 - 10:00",
    "10:00 - 11:00",
    "11:00 - 12:00",
    "12:00 - 13:00",
    "13:00 - 14:00",
    "14:00 - 15:00",
    "15:00 - 16:00",
    "16:00 - 17:00",
    "17:00 - 18:00"
]

class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ['id', 'name', 'lab_code', 'capacity', 'availability']

class TimetableSlotSerializer(serializers.ModelSerializer):
    degree_name = serializers.CharField(source='degree.degreeProgram', read_only=True)
    module_code = serializers.CharField(source='module.module_code', read_only=True)
    module_name = serializers.CharField(source='module.module_name', read_only=True)
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    lab_code = serializers.CharField(source='lab.lab_code', read_only=True)
    
    class Meta:
        model = TimetableSlot
        fields = [
            'id',
            'degree',
            'degree_name',
            'module',
            'module_code',
            'module_name',
            'lab',
            'lab_name',
            'lab_code',
            'slot_date',
            'day_of_week',
            'time_range',
            'note',
            'created_at',
            'updated_at'
        ]

class LabTimetableRangeSerializer(serializers.Serializer):
    lab_id = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        
        # Check date range doesn't exceed 30 days
        date_diff = (data['end_date'] - data['start_date']).days
        if date_diff > 30:
            raise serializers.ValidationError("Date range cannot exceed 30 days")
        
        return data

class FreeSlotSerializer(serializers.Serializer):
    slot_date = serializers.DateField()
    time_range = serializers.CharField()
    status = serializers.CharField(default="FREE")
    lab_id = serializers.IntegerField()
    lab_name = serializers.CharField()

class LabTimetableResponseSerializer(serializers.Serializer):
    lab = LabSerializer()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_days = serializers.IntegerField()
    total_slots = serializers.IntegerField()
    booked_slots = serializers.IntegerField()
    free_slots = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    timetable = serializers.DictField()