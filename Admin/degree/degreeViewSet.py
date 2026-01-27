from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Degree
from ..serializers.degree import (
    DegreeSerializer, 
    DegreeWithModulesSerializer, 
    DegreeModuleSyncSerializer, 
    DegreeSearchSerializer
)

from rest_framework.permissions import IsAuthenticated, AllowAny

class DegreeViewSet(viewsets.ModelViewSet):
    """
    Unified ViewSet for Degree operations.
    Replaces: DegreeView, DegreeUpdateView, DegreeSearchView
    """
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search']:
            return [AllowAny()]
        return [IsAuthenticated()]

    queryset = Degree.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            # Use the deep serializer for reads to include modules
            return DegreeWithModulesSerializer
        elif self.action == 'search':
            return DegreeSearchSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return DegreeModuleSyncSerializer
        return DegreeSerializer

    def get_queryset(self):
        queryset = Degree.objects.prefetch_related(
            'modules__staff_assignments__staff'
        )
        return queryset

    # Custom Action for Search matches existing path pattern
    @action(detail=False, methods=['get'])
    def search(self, request):
        search_query = request.query_params.get('search', None)
        if search_query:
            degrees = self.get_queryset().filter(degreeProgram__icontains=search_query)
        else:
            degrees = self.get_queryset()
        
        serializer = self.get_serializer(degrees, many=True)
        return Response(serializer.data)
