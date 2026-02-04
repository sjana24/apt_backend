from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from ..models import CourseModule, CourseStaff
from ..serializers.module import (
    CourseModuleSerializer, 
    ModuleSimpleSerializer, 
    CourseModuleSimpleSerializer 
)
from ..serializers.staff import StaffModuleDetailSerializer

class CourseModuleViewSet(viewsets.ModelViewSet):
    """
    Unified ViewSet for Course Modules.
    Handles CRUD operations.
    """
    permission_classes = [IsAuthenticated]
    queryset = CourseModule.objects.all()

    def get_serializer_class(self):
        # Determine serializer based on action
        if self.action in ['list', 'retrieve']:
            return ModuleSimpleSerializer # Use standard one for reading
        return CourseModuleSerializer # Default for create/update

    def get_queryset(self):
        # Optimize queries
        queryset = CourseModule.objects.select_related('degree').prefetch_related('staff_assignments__staff')
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """
        Only allow admins to delete modules.
        Staff/lecturers should not be able to delete modules.
        """
        if request.user.role != 'admin':
            return Response(
                {"error": "Only administrators can delete modules."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

# Specific Generic Views for custom endpoints to maintain exact URL structure if needed, 
# or mapped via ViewSet actions.

class StaffCourseDetailsView(APIView):
    """
    Retrieve all courses assigned to a specific staff member.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, staff_id):
        degree_id = request.query_params.get("degree_id")
        assignments = CourseStaff.objects.filter(staff_id=staff_id).select_related(
            'course_module',
            'course_module__degree',
        )
        if degree_id == "null":
            assignments = assignments.filter(course_module__degree__isnull=True)
        elif degree_id:
            assignments = assignments.filter(course_module__degree_id=degree_id)
        
        if not assignments.exists():
            return Response([], status=200)

        serializer = StaffModuleDetailSerializer(assignments, many=True)
        return Response(serializer.data)
