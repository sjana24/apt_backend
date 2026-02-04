from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import CourseStaff
from ..serializers.staff import CourseStaffSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Staff-to-Module assignments.
    """
    queryset = CourseStaff.objects.all()
    serializer_class = CourseStaffSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        """
        Allow staff to delete their own assignments.
        Admins can delete any assignment.
        """
        assignment = self.get_object()
        
        # Check if user is admin or the assignment belongs to them
        if request.user.role == 'admin' or assignment.staff.id == request.user.id:
            return super().destroy(request, *args, **kwargs)
        
        return Response(
            {"error": "You can only delete your own assignments."},
            status=status.HTTP_403_FORBIDDEN
        )
