from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Authenticate.models import UserTable
from .serializer import StaffSerializer

class StaffView(APIView):
    
    # 1. READ (GET) - Get all staff or one specific staff
    def get(self, request, pk=None):
        if pk:
            # Only get if they are actually a staff member
            staff = get_object_or_404(UserTable, pk=pk, role='staff')
            serializer = StaffSerializer(staff)
            return Response(serializer.data)
        
        # Filter ORM to only return staff roles
        staff_members = UserTable.objects.filter(role='staff')
        serializer = StaffSerializer(staff_members, many=True)
        return Response(serializer.data)

    # 2. UPDATE (PUT) - Update staff details (e.g., full_name or is_active)
    def put(self, request, pk):
        staff = get_object_or_404(UserTable, pk=pk, role='staff')
        serializer = StaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. DELETE - Remove a staff member
    def delete(self, request, pk):
        staff = get_object_or_404(UserTable, pk=pk, role='staff')
        staff.delete()
        return Response({"message": "Staff member removed successfully"}, status=status.HTTP_204_NO_CONTENT)