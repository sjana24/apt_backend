from rest_framework import serializers
from ..models import *
from ..lab.labSerializer import *
from ..degree.degreeSerializer import *
from ..course.courseSerializer import *


class TimetableSlotWriteSerializer(serializers.ModelSerializer):
    day_of_week = serializers.IntegerField(required=False, allow_null=True)
    
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
        # Automatically set day_of_week from slot_date
        slot_date = validated_data.get('slot_date')
        if slot_date:
            validated_data['day_of_week'] = slot_date.isoweekday()
            
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)



class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = '__all__'

class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = '__all__'

class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = '__all__'

class CourseStaffSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    staff_id = serializers.CharField(source='staff.id', read_only=True)
    module_name = serializers.CharField(source='course_module.module_name', read_only=True)
    
    class Meta:
        model = CourseStaff
        fields = '__all__'

class TimetableSlotCreateSerializer(serializers.ModelSerializer):
    day_of_week = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = TimetableSlot
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def create(self, validated_data):
        # Automatically set day_of_week from slot_date
        slot_date = validated_data.get('slot_date')
        if slot_date:
            validated_data['day_of_week'] = slot_date.isoweekday()
        
        # Set created_by to current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Update day_of_week if slot_date changes
        slot_date = validated_data.get('slot_date', instance.slot_date)
        if slot_date != instance.slot_date:
            validated_data['day_of_week'] = slot_date.isoweekday()
        
        return super().update(instance, validated_data)

class TimetableRangeRequestSerializer(serializers.Serializer):
    degree_id = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data

class TimetableSlotSerializer(serializers.ModelSerializer):
    degree_name = serializers.CharField(source='degree.degreeProgram', read_only=True)
    module_code = serializers.CharField(source='module.module_code', read_only=True)
    module_name = serializers.CharField(source='module.module_name', read_only=True)
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    lab_code = serializers.CharField(source='lab.lab_code', read_only=True)
    staff_list = serializers.SerializerMethodField(read_only=True)
    primary_staff = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = TimetableSlot
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_staff_list(self, obj):
        """Get all staff assigned to this module"""
        if obj.module:
            course_staffs = CourseStaff.objects.filter(course_module=obj.module)
            staff_data = []
            for course_staff in course_staffs:
                if course_staff.staff:
                    staff_data.append({
                        'staff_id': course_staff.staff.id,
                        'staff_name': course_staff.staff.full_name,
                        'role': course_staff.role,
                        'assigned_at': course_staff.assigned_at
                    })
            return staff_data
        return []
    
    def get_primary_staff(self, obj):
        """Get primary staff (first assigned or with specific role)"""
        if obj.module:
            # You can customize the logic to determine primary staff
            # Option 1: First assigned staff
            course_staff = CourseStaff.objects.filter(course_module=obj.module).first()
            
            # Option 2: Staff with 'Lead Lecturer' role
            # course_staff = CourseStaff.objects.filter(
            #     course_module=obj.module, 
            #     role='Lead Lecturer'
            # ).first()
            
            if course_staff and course_staff.staff:
                return {
                    'staff_id': course_staff.staff.id,
                    'staff_name': course_staff.staff.full_name,
                    'role': course_staff.role
                }
        return None