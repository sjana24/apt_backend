from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Lab, TimetableSlot
from ..serializers.lab import LabSerializer

class LabViewSet(viewsets.ModelViewSet):
    """
    Unified ViewSet for Lab operations.
    Handles CRUD and availability checks.
    """
    permission_classes = [IsAuthenticated]
    queryset = Lab.objects.all()
    serializer_class = LabSerializer

    @action(detail=False, methods=['get'], url_path='staff')
    def available_labs(self, request):
        """
        Custom action for staff to see available labs.
        Path: /labs/staff
        """
        labs = self.get_queryset().filter(availability=True)
        serializer = self.get_serializer(labs, many=True)
        return Response(serializer.data)

# Keep the specialized Availability view separate as it has complex logic 
# logic logic logic distinct from standard CRUD. 
# It can remain as APIView or be a ViewSet, but APIView is fine for complex custom logic.
# I will retain the logic from LabAvailabilityView in `labAvailabilityView.py` to keep this clean.
