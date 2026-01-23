from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Degree
from rest_framework.permissions import IsAuthenticated
from .degreeSerializer import *

class DegreeView(APIView):
    """
    CRUD operations for degree programs.
    GET: List all degrees or get a specific degree with modules and staff assignments
    POST: Create a new degree program
    """
    permission_classes = [IsAuthenticated]
    
    # 1. GET (List all or Retrieve one)
    def get(self, request, pk=None):
        if pk:
            # Optimize with prefetch for modules and their staff
            degree = get_object_or_404(
                Degree.objects.prefetch_related(
                    'modules__staff_assignments__staff'
                ),
                pk=pk
            )
            serializer = DegreeDeepSerializer(degree)
            return Response(serializer.data)
        
        # Optimize query for listing all degrees with their modules and staff
        degrees = Degree.objects.prefetch_related(
            'modules__staff_assignments__staff'
        )
        serializer = DegreeDeepSerializer(degrees, many=True)
        return Response(serializer.data)

    # 2. POST (Create)
    def post(self, request):
        serializer = DegreeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. PUT (Update)
class DegreeUpdateView(APIView):
    """
    Update a degree program with new modules.
    PUT: Sync degree modules by providing a list of module IDs
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        degree = get_object_or_404(Degree, pk=pk)
        
        # We use the 'Sync' serializer which only expects module_ids
        serializer = DegreeModuleSyncSerializer(degree, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Degree and modules updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#  get single staff degree details
class StaffAssignmentsByDegreeView(APIView):
    """
    Get all degree-module assignments for a specific staff member.
    Includes module and degree information for each assignment.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, staff_id):
        # 1. Look for all assignments belonging to this staff ID
        # 2. Join with course_module and degree for performance
        assignments = CourseStaff.objects.filter(staff_id=staff_id).select_related(
            'course_module__degree'
        )
        
        if not assignments.exists():
            return Response([], status=200)

        serializer = StaffModuleDetailSerializer(assignments, many=True)
        return Response(serializer.data)

class DegreeSearchView(APIView):
    """
    Search degree programs by name.
    GET: List all degrees or search by degreeProgram name
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        # Handle retrieving a single degree by ID
        if pk:
            degree = get_object_or_404(Degree, pk=pk)
            serializer = DegreeSearchSerializer(degree)
            return Response(serializer.data)
        
        # Get the 'search' parameter from the URL (e.g., /degrees/?search=CS)
        search_query = request.query_params.get('search', None)
        
        if search_query:
            # Filter degrees where degreeProgram contains the search text (case-insensitive)
            degrees = Degree.objects.filter(degreeProgram__icontains=search_query)
        else:
            degrees = Degree.objects.all()

        serializer = DegreeSearchSerializer(degrees, many=True)
        return Response(serializer.data)
