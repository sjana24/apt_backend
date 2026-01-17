from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CourseModule
# from .serializer import *
from .courseSerializer import *
from rest_framework.permissions import IsAuthenticated

class CourseModuleView(APIView):
    permission_classes = [IsAuthenticated] 
    # 1. CREATE (POST)
    def post(self, request):
        serializer = CreateModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. READ (GET) - Get all or get one
    def get(self, request, pk=None):
        if pk:
            module = get_object_or_404(CourseModule, pk=pk)
            serializer = ModuleSimpleSerializer(module)
            return Response(serializer.data)
        
        modules = CourseModule.objects.all()
        serializer = ModuleSimpleSerializer(modules, many=True)
        return Response(serializer.data)
class StaffCourseDetailsView(APIView):
    def get(self, request, staff_id):
        # Fetch all assignments for this staff, including related module and degree
        assignments = CourseStaff.objects.filter(staff_id=staff_id).select_related(
            'course_module__degree'
        )
        
        # If the staff has no assignments, return an empty list
        if not assignments.exists():
            return Response([], status=200)

        serializer = StaffAssignmentDetailSerializer(assignments, many=True)
        return Response(serializer.data)

    # # 3. UPDATE (PUT)
class CourseModuleUpdateView(APIView):
    def put(self, request, pk):
        module = get_object_or_404(CourseModule, pk=pk)
        
        # Use partial=True to allow updating only specific parts
        serializer = ModuleUpdateSerializer(module, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    # # 4. DELETE
    # def delete(self, request, pk):
    #     module = get_object_or_404(CourseModule, pk=pk)
    #     module.delete()
    #     return Response({"message": "Module deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

