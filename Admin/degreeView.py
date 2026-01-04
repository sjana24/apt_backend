from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Degree
from .serializer import *
from rest_framework.permissions import IsAuthenticated

class DegreeView(APIView):
    permission_classes = [IsAuthenticated] 
    # 1. GET (List all or Retrieve one)
    def get(self, request, pk=None):
        if pk:
            degree = get_object_or_404(Degree, pk=pk)
            serializer = DegreeSerializer(degree)
            return Response(serializer.data)
        
        degrees = Degree.objects.all()
        serializer = DegreeSerializer(degrees, many=True)
        return Response(serializer.data)

    # 2. POST (Create)
    def post(self, request):
        serializer = DegreeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. PUT (Update)
    def put(self, request, pk):
        degree = get_object_or_404(Degree, pk=pk)
        # partial=True allows updating just the level or semester without sending everything
        serializer = DegreeSerializer(degree, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 4. DELETE
    def delete(self, request, pk):
        degree = get_object_or_404(Degree, pk=pk)
        degree.delete()
        return Response({"message": "Degree program deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class DegreeDetailWithModulesView(APIView):
    permission_classes = [IsAuthenticated] 
    def get(self, request, degree_id):
        # Fetch the specific degree or return 404
        degree = get_object_or_404(Degree, pk=degree_id)
        
        # Serialize the degree (which now includes the module list)
        # serializer = DegreeWithModulesSerializer(degree)
        
        # return Response("data")