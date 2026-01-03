from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.contrib.auth import authenticate

class UserView(APIView):
    def post(self, request):
        # 1. Extract data from the request
        data = request.data
        email = data.get('email')
        full_name = data.get('full_name')
        password = data.get('password')
        role = data.get('role', 'staff') # Default to staff if not provided

        # 2. Basic Validation (In a real app, use a Serializer for this!)
        if not email or not password or not full_name:
            return Response(
                {"error": "Email, full_name, and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 3. Use the Manager to create the user
            # This triggers UserTableManager.create_user()
            user = UserTable.objects.create_user(
                email=email,
                full_name=full_name,
                password=password,
                role=role
            )

            return Response({
                "message": "User created successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
class UserLoginView(APIView):
    def post(self,request):
        data = request.data
        userEmail = data.get('email')
        userPassword = data.get('password')

        if not userEmail or not userPassword :
            return Response(
                {"error": "Email password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:

            user_verification =authenticate(ëmail = userEmail ,password = userPassword)

            return Response({
                "message": "User created successfully",
                "user": user_verification

            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )