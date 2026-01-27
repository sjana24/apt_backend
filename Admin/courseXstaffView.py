from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CourseStaff
from .serializers.staff import StaffModuleDetailSerializer

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