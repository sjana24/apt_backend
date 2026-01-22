# views.py
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from Admin.models import Lab, TimetableSlot, CourseModule
from .serializer import *
from .timeTableSerializersByLab import *
from Admin.timeTableSerializers import TimetableSlotWriteSerializer

class TimetableSlotLabViewSet(ViewSet):
    """
    ViewSet for handling timetable slots with lab-specific endpoints
    """
    
    @action(detail=False, methods=['post'], url_path='by-lab')
    def by_lab(self, request):
        """
        LAB-WISE FULL TIMETABLE (Booked + Free slots)
        Returns complete timetable for a lab including both booked and free time slots.
        """
        serializer = LabTimetableRangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lab_id = serializer.validated_data['lab_id']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        lab = get_object_or_404(Lab, id=lab_id)
        
        if not lab.availability:
            return Response({
                "error": f"Lab {lab.name} is currently unavailable",
                "lab": LabSerializer(lab).data
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch booked slots
        booked_slots = TimetableSlot.objects.filter(
            lab=lab,
            slot_date__gte=start_date,
            slot_date__lte=end_date
        ).select_related('degree', 'module', 'lab').order_by('slot_date', 'time_range')

        booked_map = {}
        for slot in booked_slots:
            key = (slot.slot_date, slot.time_range)
            booked_map[key] = slot

        timetable = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            day_slots = []

            for time_range in LAB_TIME_SLOTS:
                key = (current_date, time_range)

                if key in booked_map:
                    slot = booked_map[key]
                    slot_data = TimetableSlotSerializer(slot).data
                    slot_data['status'] = 'BOOKED'
                    day_slots.append(slot_data)
                else:
                    free_slot = {
                        "slot_date": current_date,
                        "time_range": time_range,
                        "status": "FREE",
                        "lab_id": lab.id,
                        "lab_name": lab.name,
                        "lab_code": lab.lab_code,
                        "capacity": lab.capacity,
                        "note": "Available for booking"
                    }
                    day_slots.append(free_slot)

            timetable[date_key] = day_slots
            current_date += timedelta(days=1)

        total_days = (end_date - start_date).days + 1
        total_time_slots = total_days * len(LAB_TIME_SLOTS)
        booked_count = len(booked_slots)
        free_count = total_time_slots - booked_count
        occupancy_rate = (booked_count / total_time_slots * 100) if total_time_slots > 0 else 0

        response_data = {
            "lab": LabSerializer(lab).data,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "total_slots": total_time_slots,
            "booked_slots": booked_count,
            "free_slots": free_count,
            "occupancy_rate": round(occupancy_rate, 2),
            "timetable": timetable
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='by-lab/available')
    def by_lab_available_only(self, request):
        """
        Get only available (FREE) time slots for a lab
        """
        serializer = LabTimetableRangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lab_id = serializer.validated_data['lab_id']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        lab = get_object_or_404(Lab, id=lab_id, availability=True)

        booked_slots = TimetableSlot.objects.filter(
            lab=lab,
            slot_date__gte=start_date,
            slot_date__lte=end_date
        ).values_list('slot_date', 'time_range')

        booked_set = set(booked_slots)
        available_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            for time_range in LAB_TIME_SLOTS:
                if (current_date, time_range) not in booked_set:
                    available_slots.append({
                        "slot_date": current_date,
                        "time_range": time_range,
                        "lab_id": lab.id,
                        "lab_name": lab.name,
                        "lab_code": lab.lab_code,
                        "capacity": lab.capacity,
                        "status": "AVAILABLE"
                    })
            current_date += timedelta(days=1)

        return Response({
            "lab": LabSerializer(lab).data,
            "start_date": start_date,
            "end_date": end_date,
            "total_available_slots": len(available_slots),
            "available_slots": available_slots
        })

    @action(detail=False, methods=['post'], url_path='check-slot')
    def check_slot_availability(self, request):
        """
        Check specific time slot availability
        """
        lab_id = request.data.get('lab_id')
        slot_date = request.data.get('slot_date')
        time_range = request.data.get('time_range')

        if not all([lab_id, slot_date, time_range]):
            return Response({
                "error": "lab_id, slot_date, and time_range are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            return Response({
                "error": "Lab not found"
            }, status=status.HTTP_404_NOT_FOUND)

        if not lab.availability:
            return Response({
                "available": False,
                "reason": "Lab is not available",
                "lab": LabSerializer(lab).data
            })

        is_booked = TimetableSlot.objects.filter(
            lab=lab,
            slot_date=slot_date,
            time_range=time_range
        ).exists()

        if is_booked:
            return Response({
                "available": False,
                "reason": "Time slot is already booked",
                "lab": LabSerializer(lab).data
            })

        return Response({
            "available": True,
            "lab": LabSerializer(lab).data,
            "slot_date": slot_date,
            "time_range": time_range,
            "message": "Slot is available for booking"
        })

    def create(self, request):
        """
        Create a new timetable slot
        """
        serializer = TimetableSlotWriteSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Keep your original APIView for simple CRUD operations
from rest_framework.views import APIView
from rest_framework.generics import DestroyAPIView

class TimetableSlotListCreateAPIView(APIView):
    """
    Simple APIView for basic timetable slot operations
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

class TimetableSlotDetailAPIView(DestroyAPIView):
    """
    Delete a timetable slot
    """
    queryset = TimetableSlot.objects.all()
    serializer_class = TimetableSlotWriteSerializer