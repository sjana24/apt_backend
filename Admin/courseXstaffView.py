# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import CourseStaff, CourseModule
# from .serializer import CourseStaffSerializer

# class CourseStaffView(APIView):
    
#     # 1. GET: List all assignments or assignments for a specific module
#     def get(self, request):
#         module_id = request.query_params.get('module_id')
#         if module_id:
#             assignments = CourseStaff.objects.filter(course_module_id=module_id)
#         else:
#             assignments = CourseStaff.objects.all()
            
#         serializer = CourseStaffSerializer(assignments, many=True)
#         return Response(serializer.data)

#     # 2. POST: Assign a Staff member to a Module
#     def post(self, request):
#         serializer = CourseStaffSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#    # 3. PUT: Update an assignment (e.g., change the role)
#     def put(self, request, pk):
#         assignment = get_object_or_404(CourseStaff, pk=pk)
        
#         # partial=True allows you to update just the 'role' without sending everything
#         serializer = CourseStaffSerializer(assignment, data=request.data, partial=True)
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     # 4. DELETE: Remove an assignment
#     def delete(self, request, pk):
#         assignment = get_object_or_404(CourseStaff, pk=pk)
#         assignment.delete()
#         return Response({"message": "Staff assignment removed"}, status=status.HTTP_204_NO_CONTENT)