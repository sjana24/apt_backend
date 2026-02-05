from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models import TimetableSlot
from .timeTableSerializers import *
from .timeTableSerializers import (
    # TimetableSlotGetSerializer,
    TimetableSlotWriteSerializer
)

class TimetableSlotListCreateAPIView(APIView):
    """
    API view for creating timetable slots.
    POST: Create a new timetable slot with validation
    """

    def post(self, request):
        serializer = TimetableSlotWriteSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TimetableSlotDetailAPIView(APIView):
    """
    API view for deleting timetable slots.
    DELETE: Remove a specific timetable slot
    """

    def delete(self, request, pk):
        slot = get_object_or_404(TimetableSlot, pk=pk)
        slot.delete()
        return Response(
            {"message": "Timetable slot deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    









    
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
from ..models import Degree, CourseModule, Lab, CourseStaff, TimetableSlot
from .timeTableSerializers import (
    DegreeSerializer, CourseModuleSerializer, LabSerializer, 
    CourseStaffSerializer, TimetableSlotSerializer, 
    TimetableSlotCreateSerializer, TimetableRangeRequestSerializer, TimetableSlotWriteSerializer
)

# Degree ViewSet
class DegreeViewSet(viewsets.ModelViewSet):
    queryset = Degree.objects.all()
    serializer_class = DegreeSerializer
    permission_classes = [IsAuthenticated]

# CourseModule ViewSet
class CourseModuleViewSet(viewsets.ModelViewSet):
    queryset = CourseModule.objects.all()
    serializer_class = CourseModuleSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_degree(self, request):
        degree_id = request.query_params.get('degree_id')
        if degree_id:
            modules = CourseModule.objects.filter(degree_id=degree_id)
            serializer = self.get_serializer(modules, many=True)
            return Response(serializer.data)
        return Response([])

# Lab ViewSet
class LabViewSet(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    permission_classes = [IsAuthenticated]

# CourseStaff ViewSet
class CourseStaffViewSet(viewsets.ModelViewSet):
    queryset = CourseStaff.objects.all()
    serializer_class = CourseStaffSerializer
    permission_classes = [IsAuthenticated]

from django.db.models import Sum

from rest_framework.permissions import IsAuthenticated, AllowAny

# Janakan -- start
# TimetableSlot ViewSet
class TimetableSlotViewSet(viewsets.ModelViewSet):
    queryset = TimetableSlot.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_range']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TimetableSlotCreateSerializer
        return TimetableSlotSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by degree if provided
        degree_id = self.request.query_params.get('degree_id')
        if degree_id:
            queryset = queryset.filter(degree_id=degree_id)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                slot_date__gte=start_date,
                slot_date__lte=end_date
            )
        
        # Filter by specific date if provided
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(slot_date=date)
        
        return queryset
#  jana end---
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get summary stats for the staff dashboard"""
        user = request.user
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # 1. Modules assigned to this staff
        assigned_module_ids = CourseStaff.objects.filter(staff=user).values_list('course_module_id', flat=True)
        
        # 2. Upcoming sessions today
        upcoming_count = TimetableSlot.objects.filter(
            module_id__in=assigned_module_ids,
            slot_date=today
        ).count()
        
        # 3. Pending sessions (all sessions this week for assigned modules)
        pending_sessions = TimetableSlot.objects.filter(
            module_id__in=assigned_module_ids,
            slot_date__gte=today,
            slot_date__lte=end_of_week
        ).count()
        
        # 4. Available labs today (total available labs right now)
        available_labs = Lab.objects.filter(availability=True).count()
        
        # 5. Booked hours (sum of credits for assigned modules)
        total_credits = CourseModule.objects.filter(id__in=assigned_module_ids).aggregate(Sum('credit'))['credit__sum'] or 0
        
        return Response({
            'upcoming': upcoming_count,
            'pending': pending_sessions,
            'available': available_labs,
            'bookedHours': total_credits
        })

    @action(detail=False, methods=['get'])
    def my_schedule(self, request):
        """Get top 10 upcoming sessions for the logged-in staff"""
        user = request.user
        today = datetime.now().date()
        
        assigned_module_ids = CourseStaff.objects.filter(staff=user).values_list('course_module_id', flat=True)
        slots = TimetableSlot.objects.filter(
            module_id__in=assigned_module_ids,
            slot_date__gte=today
        ).order_by('slot_date', 'time_range')[:10]
        
        serializer = TimetableSlotSerializer(slots, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def get_range(self, request):
        """Get timetable slots for a specific degree and date range"""
        serializer = TimetableRangeRequestSerializer(data=request.data)
        if serializer.is_valid():
            degree_id = serializer.validated_data['degree_id']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']
            
            # Get the degree
            degree = get_object_or_404(Degree, id=degree_id)
            
            # Get slots within date range
            slots = TimetableSlot.objects.filter(
                degree=degree,
                slot_date__gte=start_date,
                slot_date__lte=end_date
            ).order_by('slot_date', 'time_range')
            
            # Group slots by day for better frontend consumption
            timetable_data = {}
            for slot in slots:
                day = slot.slot_date.strftime('%Y-%m-%d')
                if day not in timetable_data:
                    timetable_data[day] = []
                
                slot_data = TimetableSlotSerializer(slot).data
                timetable_data[day].append(slot_data)
            
            # Add empty days in the range
            current_date = start_date
            while current_date <= end_date:
                day_str = current_date.strftime('%Y-%m-%d')
                if day_str not in timetable_data:
                    timetable_data[day_str] = []
                current_date += timedelta(days=1)
            
            # Sort by date
            sorted_timetable = dict(sorted(timetable_data.items()))
            
            response_data = {
                'degree': DegreeSerializer(degree).data,
                'start_date': start_date,
                'end_date': end_date,
                'timetable': sorted_timetable,
                'total_slots': slots.count()
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'post'])
    def check_availability(self, request):
        """
        Check lab availability.
        If lab_id is provided: Check specific lab.
        If no lab_id: Return list of all available labs for that slot.
        """
        lab_id = request.query_params.get('lab_id') or request.data.get('lab_id')
        slot_date = request.query_params.get('date') or request.data.get('date') # Frontend uses 'date' param
        time_range = request.query_params.get('time_range') or request.data.get('time_range')
        
        if not slot_date or not time_range:
             return Response({
                'error': 'Missing parameters: date and time_range are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Legacy/Specific check
        if lab_id:
            lab = get_object_or_404(Lab, id=lab_id)
            if not lab.availability:
                return Response({
                    'available': False,
                    'message': f'Lab {lab.name} is not available'
                })
            
            conflicting_slot = TimetableSlot.objects.filter(
                lab_id=lab_id,
                slot_date=slot_date,
                time_range=time_range
            ).exists()
            
            if conflicting_slot:
                return Response({
                    'available': False,
                    'message': f'Lab {lab.name} is already booked'
                })
            
            return Response({
                'available': True,
                'message': f'Lab {lab.name} is available'
            })

        # Feature: List all available labs
        booked_lab_ids = TimetableSlot.objects.filter(
            slot_date=slot_date,
            time_range=time_range
        ).values_list('lab_id', flat=True)
        
        available_labs = Lab.objects.exclude(id__in=booked_lab_ids).filter(availability=True)
        serializer = LabSerializer(available_labs, many=True)
        return Response({'labs': serializer.data})