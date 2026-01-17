from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Degree
# from .serializer import *
from rest_framework.permissions import IsAuthenticated

from .degreeSerializer import *

class DegreeView(APIView):
    permission_classes = [IsAuthenticated] 
    # 1. GET (List all or Retrieve one)
    def get(self, request, pk=None):
        if pk:
            degree = get_object_or_404(Degree, pk=pk)
            serializer = DegreeDeepSerializer(degree)
            return Response(serializer.data)
        
        degrees = Degree.objects.all()
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
    

 
    # # 4. DELETE
    # def delete(self, request, pk):
    #     degree = get_object_or_404(Degree, pk=pk)
    #     degree.delete()
    #     return Response({"message": "Degree program deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
#  get single staff degree details
class StaffAssignmentsByDegreeView(APIView):
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
    permission_classes = [IsAuthenticated] 
    def get(self, request, pk=None):
        # Handle retrieving a single degree by ID
        if pk:
            degree = get_object_or_404(Degree, pk=pk)
            serializer = DegreeSearchSerializer(degree)
            return Response(serializer.data)
        
        # --- SEARCH LOGIC START ---
        # Get the 'search' parameter from the URL (e.g., /degrees/?search=CS)
        search_query = request.query_params.get('search', None)
        
        if search_query:
            # Filter degrees where degreeProgram contains the search text (case-insensitive)
            degrees = Degree.objects.filter(degreeProgram__icontains=search_query)
        else:
            degrees = Degree.objects.all()
        # --- SEARCH LOGIC END ---

        serializer = DegreeSearchSerializer(degrees, many=True)
        return Response(serializer.data)
