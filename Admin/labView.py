# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Lab
# from .serializer import LabSerializer

# class LabView(APIView):
    
#     def get(self, request, pk=None):
#         if pk:
#             lab = get_object_or_404(Lab, pk=pk)
#             serializer = LabSerializer(lab)
#             return Response(serializer.data)
        
#         labs = Lab.objects.all()
#         serializer = LabSerializer(labs, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = LabSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         lab = get_object_or_404(Lab, pk=pk)
#         serializer = LabSerializer(lab, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         lab = get_object_or_404(Lab, pk=pk)
#         lab.delete()
#         return Response({"message": "Lab deleted successfully"}, status=status.HTTP_204_NO_CONTENT)