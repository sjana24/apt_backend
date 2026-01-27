from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Authenticate.models import UserTable
from ..serializers.staff import StaffSerializer

class StaffViewSet(viewsets.ModelViewSet):
    """
    Unified ViewSet for Staff operations.
    Handles CRUD for staff members and their assignments.
    """
    permission_classes = [IsAuthenticated]
    queryset = UserTable.objects.filter(role='staff')
    serializer_class = StaffSerializer

    def get_queryset(self):
        # Optimize query: filter only staff and prefetch assignments
        return UserTable.objects.filter(role='staff').prefetch_related(
            'module_assignments__course_module'
        )

    def update(self, request, *args, **kwargs):
        # Default update behavior fits most needs, but original had partial=True specific logic
        # ModelViewSet update() handles this, but let's ensure partial is allowed
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
