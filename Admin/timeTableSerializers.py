from rest_framework import serializers
from .models import (
    Degree,
    CourseModule,
    Lab,
    CourseStaff,
    TimetableSlot
)
from Authenticate.models import UserTable
from .labSerializer import *
from .degreeSerializer import *
from .courseSerializer import *

class TimetableSlotGetSerializer(serializers.ModelSerializer):
    degree = DegreeSerializer(read_only=True)
    module = CourseModuleSerializer(read_only=True)
    lab = LabSerializer(read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True
    )

    class Meta:
        model = TimetableSlot
        fields = [
            'id',
            'degree',
            'module',
            'lab',
            'slot_date',
            'day_of_week',
            'day_of_week_display',
            'time_range',
            'note',
            'created_by',
            'created_at',
            'updated_at'
        ]

class TimetableSlotWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableSlot
        fields = [
            'degree',
            'module',
            'lab',
            'slot_date',
            'day_of_week',
            'time_range',
            'note'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

