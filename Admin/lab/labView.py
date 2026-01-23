from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, date
from ..models import Lab, TimetableSlot, Degree, CourseModule
from .labSerializer import LabSerializer, LabAvailabilityRequestSerializer, AvailableLabSerializer


class LabViewStaff(APIView):
    """
    View for staff to retrieve available labs.
    GET: List only available labs, optionally filtered by lab ID
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        # If a specific lab is requested
        if pk:
            lab = get_object_or_404(Lab, pk=pk, availability=True)
            serializer = LabSerializer(lab)
            return Response(serializer.data)

        # If no pk, return only available labs
        labs = Lab.objects.filter(availability=True)
        serializer = LabSerializer(labs, many=True)
        return Response(serializer.data)


class LabView(APIView):
    """
    Full CRUD operations for labs.
    GET: List all labs or get a specific lab
    POST: Create a new lab
    PUT: Update lab details
    DELETE: Remove a lab
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        if pk:
            lab = get_object_or_404(Lab, pk=pk)
            serializer = LabSerializer(lab)
            return Response(serializer.data)
        
        labs = Lab.objects.all()
        serializer = LabSerializer(labs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LabSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        lab = get_object_or_404(Lab, pk=pk)
        serializer = LabSerializer(lab, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        lab = get_object_or_404(Lab, pk=pk)
        lab.delete()
        return Response({"message": "Lab deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class LabAvailabilityView(APIView):
    """View for checking lab availability based on TimetableSlot model"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        """
        Check lab availability for a specific date and time
        Query parameters:
        - date: YYYY-MM-DD (required) - The date to check
        - time_range: HH:MM-HH:MM or HH:MM - HH:MM (required) - Time slot to check
        - degree_id: (optional) - Filter by specific degree
        - module_id: (optional) - Filter by specific module
        - exclude_slot_id: (optional) - Exclude a specific timetable slot (useful for updates)
        - exclude_lab_id: (optional) - Exclude a specific lab (useful for lab swapping)
        """
        
        # Validate request parameters
        request_serializer = LabAvailabilityRequestSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = request_serializer.validated_data
        check_date = validated_data['date']
        time_range = validated_data['time_range']  # Already normalized
        degree = validated_data.get('degree')
        module = validated_data.get('module')
        
        # Get optional exclusion parameters
        exclude_slot_id = request.query_params.get('exclude_slot_id')
        exclude_lab_id = request.query_params.get('exclude_lab_id')
        
        # Start building the conflict query
        conflict_query = TimetableSlot.objects.filter(
            slot_date=check_date,
            time_range=time_range
        )
        
        # Exclude specific slot if provided (for update operations)
        if exclude_slot_id and exclude_slot_id.isdigit():
            conflict_query = conflict_query.exclude(id=int(exclude_slot_id))
        
        # Exclude specific lab if provided (for lab swapping)
        if exclude_lab_id and exclude_lab_id.isdigit():
            conflict_query = conflict_query.exclude(lab_id=int(exclude_lab_id))
        
        # Get IDs of labs that are already booked at this time
        booked_lab_ids = list(conflict_query.values_list('lab_id', flat=True).distinct())
        
        # Start building labs query
        labs_query = Lab.objects.all()
        
        # Filter by specific lab if pk provided
        if pk:
            labs_query = labs_query.filter(id=pk)
            if not labs_query.exists():
                return Response(
                    {"error": f"Lab with ID {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Additional filters (active labs, etc.)
        labs_query = labs_query.filter(availability=True)  # Only available labs
        
        # Get all labs
        labs = labs_query.order_by('name')
        
        # Prepare response data for each lab
        labs_data = []
        for lab in labs:
            # Check if this lab is booked
            is_booked = lab.id in booked_lab_ids
            
            # If booked, get the booking details
            conflict_details = None
            if is_booked:
                booking = conflict_query.filter(lab=lab).first()
                if booking:
                    conflict_details = {
                        'booking_id': booking.id,
                        'degree': {
                            'id': booking.degree.id,
                            'name': booking.degree.degreeProgram
                        } if booking.degree else None,
                        'module': {
                            'id': booking.module.id if booking.module else None,
                            'name': booking.module.module_name if booking.module else None,
                            'code': booking.module.module_code if booking.module else None
                        },
                        'time_range': booking.time_range,
                        'note': booking.note,
                        'created_at': booking.created_at
                    }
            
            # Serialize lab data
            lab_data = AvailableLabSerializer(lab, context={'request': request}).data
            lab_data['is_available'] = not is_booked
            lab_data['conflict_details'] = conflict_details
            
            # Add additional availability context
            if degree and not is_booked:
                # Check if this lab is suitable for the degree (you might have additional logic here)
                lab_data['suitable_for_degree'] = True
            else:
                lab_data['suitable_for_degree'] = False
            
            labs_data.append(lab_data)
        
        # Prepare response metadata
        response_metadata = {
            'query': {
                'date': check_date.strftime('%Y-%m-%d'),
                'time_range': time_range,
                'degree_id': degree.id if degree else None,
                'module_id': module.id if module else None,
            },
            'availability_summary': {
                'total_labs_checked': labs.count(),
                'available_labs': len([lab for lab in labs_data if lab['is_available']]),
                'occupied_labs': len([lab for lab in labs_data if not lab['is_available']]),
            },
            'filters_applied': {
                'lab_id': pk,
                'exclude_slot_id': exclude_slot_id,
                'exclude_lab_id': exclude_lab_id,
                'only_available_labs': True,
            }
        }
        
        # Return response
        if pk:
            # Single lab response
            if labs_data:
                return Response({
                    **labs_data[0],
                    'metadata': response_metadata
                })
            else:
                return Response(
                    {"error": "No lab found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Multiple labs response
            return Response({
                'metadata': response_metadata,
                'labs': labs_data
            })

class LabAvailabilityView1(APIView):
    """View for checking lab availability"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        """
        Get lab availability
        Query params:
        - date: YYYY-MM-DD (required)
        - time_range: HH:MM - HH:MM (required)
        - day_of_week: 1-7 (optional, will be derived from date if not provided)
        - exclude_lab_id: exclude specific lab (optional, for updating existing booking)
        """
        # Validate request parameters
        request_serializer = LabAvailabilityRequestSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = request_serializer.validated_data
        date = validated_data['date']
        time_range = validated_data['time_range']
        day_of_week = validated_data.get('day_of_week')
        
        # Get exclude_lab_id if provided (for updating existing booking)
        exclude_lab_id = request.query_params.get('exclude_lab_id')
        
        # Query for occupied labs
        occupied_query = TimetableSlot.objects.filter(
            slot_date=date,
            time_range=time_range
        )
        
        # If updating an existing booking, exclude that lab from occupied list
        if exclude_lab_id and exclude_lab_id.isdigit():
            occupied_query = occupied_query.exclude(lab_id=int(exclude_lab_id))
        
        occupied_lab_ids = occupied_query.values_list('lab_id', flat=True)
        
        # Get labs query
        if pk:
            # Specific lab
            labs = Lab.objects.filter(id=pk)
        else:
            # All labs
            labs = Lab.objects.all()
        
        # Filter out labs that are not available (maintenance, etc.)
        # Add your own filters here if needed
        # labs = labs.filter(is_active=True)
        
        # Prepare response with availability info
        result = []
        for lab in labs:
            lab_data = AvailableLabSerializer(lab, context={'request': request}).data
            lab_data['is_available'] = lab.id not in occupied_lab_ids
            
            # Add additional availability details
            if lab.id in occupied_lab_ids:
                occupied_slot = TimetableSlot.objects.filter(
                    lab=lab,
                    slot_date=date,
                    time_range=time_range
                ).first()
                
                lab_data['conflict_details'] = {
                    'module': occupied_slot.module.module_name if occupied_slot.module else None,
                    'module_code': occupied_slot.module.module_code if occupied_slot.module else None,
                    'degree': occupied_slot.degree.degreeProgram if occupied_slot.degree else None,
                    'time': occupied_slot.time_range,
                    'note': occupied_slot.note
                }
            else:
                lab_data['conflict_details'] = None
            
            result.append(lab_data)
        
        # If specific lab requested, return single object
        if pk:
            return Response(result[0] if result else {})
        
        return Response({
            'date': date,
            'time_range': time_range,
            'day_of_week': day_of_week,
            'total_labs': labs.count(),
            'available_labs': len([lab for lab in result if lab['is_available']]),
            'occupied_labs': len([lab for lab in result if not lab['is_available']]),
            'labs': result
        })