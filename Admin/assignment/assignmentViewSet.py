from rest_framework import viewsets
from ..models import CourseStaff
from ..serializers.staff import CourseStaffSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Staff-to-Module assignments.
    """
    queryset = CourseStaff.objects.all()
    serializer_class = CourseStaffSerializer
