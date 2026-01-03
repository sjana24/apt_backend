from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CourseModule
from .serializer import CourseModuleSerializer

class CourseModuleView(APIView):
    
    # 1. CREATE (POST)
    def post(self, request):
        serializer = CourseModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. READ (GET) - Get all or get one
    def get(self, request, pk=None):
        if pk:
            module = get_object_or_404(CourseModule, pk=pk)
            serializer = CourseModuleSerializer(module)
            return Response(serializer.data)
        
        modules = CourseModule.objects.all()
        serializer = CourseModuleSerializer(modules, many=True)
        return Response(serializer.data)

    # 3. UPDATE (PUT)
    def put(self, request, pk):
        module = get_object_or_404(CourseModule, pk=pk)
        # partial=True allows you to update just one field if you want
        serializer = CourseModuleSerializer(module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 4. DELETE
    def delete(self, request, pk):
        module = get_object_or_404(CourseModule, pk=pk)
        module.delete()
        return Response({"message": "Module deleted successfully"}, status=status.HTTP_204_NO_CONTENT)