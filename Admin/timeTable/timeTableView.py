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

# TimetableSlot ViewSet
class TimetableSlotViewSet(viewsets.ModelViewSet):
    queryset = TimetableSlot.objects.all()
    permission_classes = [IsAuthenticated]
    
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
    
    @action(detail=False, methods=['post'])
    def check_availability(self, request):
        """Check lab and time slot availability"""
        lab_id = request.query_params.get('lab_id')
        slot_date = request.query_params.get('slot_date')
        time_range = request.query_params.get('time_range')
        
        if lab_id and slot_date and time_range:
            # Check if lab exists and is available
            lab = get_object_or_404(Lab, id=lab_id)
            if not lab.availability:
                return Response({
                    'available': False,
                    'message': f'Lab {lab.name} is not available'
                })
            
            # Check if lab is already booked at this time
            conflicting_slot = TimetableSlot.objects.filter(
                lab_id=lab_id,
                slot_date=slot_date,
                time_range=time_range
            ).exists()
            
            if conflicting_slot:
                return Response({
                    'available': False,
                    'message': f'Lab {lab.name} is already booked at {time_range} on {slot_date}'
                })
            
            return Response({
                'available': True,
                'message': f'Lab {lab.name} is available at {time_range} on {slot_date}'
            })
        
        return Response({
            'error': 'Missing parameters: lab_id, slot_date, and time_range are required'
        }, status=status.HTTP_400_BAD_REQUEST)