from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Authenticate.models import UserTable
# from .serializer import StaffSerializer
from .staffSerializers import *

class StaffView(APIView):

    # 1. READ (GET) - Get all staff or one specific staff
    def get(self, request, pk=None):
        if pk:
            # Optimization: prefetch the assignments and the linked modules
            staff = get_object_or_404(
                UserTable.objects.prefetch_related('module_assignments__course_module'), 
                pk=pk, 
                role='staff'
            )
            serializer = StaffSerializer(staff)
            return Response(serializer.data)
    
        # Filter only staff and prefetch their modules
        staff_members = UserTable.objects.filter(role='staff').prefetch_related(
            'module_assignments__course_module'
        )
        serializer = StaffSerializer(staff_members, many=True)
        return Response(serializer.data)    


    # 2. UPDATE (PUT) - Update staff details (e.g., full_name or is_active)
    def put(self, request, pk):
            # 1. Fetch the staff member
            staff = get_object_or_404(UserTable, pk=pk, role='staff')
            
            # 2. Pass request data to the serializer
            # partial=True allows updating just name OR modules, rather than requiring all fields
            serializer = StaffUpdateSerializer(staff, data=request.data, partial=True)
            
            if serializer.is_valid():
                # 3. .save() calls the update() method in our Serializer
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    # def put(self, request, pk):
    #     staff = get_object_or_404(UserTable, pk=pk, role='staff')
    #     serializer = StaffSerializer(staff, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. DELETE - Remove a staff member
    def delete(self, request, pk):
        staff = get_object_or_404(UserTable, pk=pk, role='staff')
        staff.delete()
        return Response({"message": "Staff member removed successfully"}, status=status.HTTP_204_NO_CONTENT)