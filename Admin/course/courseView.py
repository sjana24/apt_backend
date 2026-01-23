from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import CourseModule
from .courseSerializer import *
from rest_framework.permissions import IsAuthenticated

class CourseModuleView(APIView):
    """
    CRUD operations for course modules.
    GET: List all modules or get a specific module by ID
    POST: Create a new course module
    """
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
            # Optimize with select_related for degree
            module = get_object_or_404(
                CourseModule.objects.select_related('degree'),
                pk=pk
            )
            serializer = ModuleSimpleSerializer(module)
            return Response(serializer.data)
        
        # Optimize with select_related for all modules' degrees
        modules = CourseModule.objects.select_related('degree').prefetch_related('staff_assignments__staff')
        serializer = ModuleSimpleSerializer(modules, many=True)
        return Response(serializer.data)
    
class StaffCourseDetailsView(APIView):
    """
    Retrieve all courses assigned to a specific staff member.
    Supports filtering by degree_id or modules without a degree.
    """
    
    def get(self, request, staff_id):
        # Fetch all assignments for this staff, including related module and degree
        degree_id = request.query_params.get("degree_id")
        assignments = CourseStaff.objects.filter(staff_id=staff_id).select_related(
            'course_module',
            'course_module__degree',
        )
        if degree_id == "null":
            # Only modules WITHOUT a degree
            assignments = assignments.filter(
                course_module__degree__isnull=True
            )
        elif degree_id:
            # Only modules for a specific degree
            assignments = assignments.filter(
                course_module__degree_id=degree_id
            )
        
        # If the staff has no assignments, return an empty list
        if not assignments.exists():
            return Response([], status=200)

        serializer = StaffAssignmentDetailSerializer(assignments, many=True)
        return Response(serializer.data)
class CourseModuleUpdateView(APIView):
    """
    Update a course module with new details and staff assignments.
    PUT: Update module name, code, credit, and/or staff assignments.
    """
    
    def put(self, request, pk):
        module = get_object_or_404(CourseModule, pk=pk)
        
        # Use partial=True to allow updating only specific parts
        serializer = ModuleUpdateSerializer(module, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

