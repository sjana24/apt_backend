from rest_framework import serializers
from ..models import TimetableSlot

class TimetableSlotSerializer(serializers.ModelSerializer):
    """
    Serializer for Timetable Slots.
    """
    # Show names in read operations
    degree_name = serializers.ReadOnlyField(source='degree.degreeProgram')
    module_name = serializers.ReadOnlyField(source='module.module_name')
    lab_name = serializers.ReadOnlyField(source='lab.name')

    class Meta:
        model = TimetableSlot
        fields = [
            'id', 'slot_date', 'day_of_week', 'time_range', 'note',
            'degree', 'degree_name',
            'module', 'module_name',
            'lab', 'lab_name',
            'created_by'
        ]
        read_only_fields = ['created_by']
