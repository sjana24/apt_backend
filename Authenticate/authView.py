from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.contrib.auth import authenticate,login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

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

            # user_verification =authenticate(ëmail = userEmail ,password = userPassword)
            user = authenticate(request, email=userEmail, password=userPassword)
            if user is not None:
                # 2. Use inbuilt login (this sets the session cookie)
                data=login(request, user)

                refresh = RefreshToken.for_user(user)

                serializer = UserTableSerializer(user)

                return Response({
                "message": "Login successful",
                "user": {
                    "user": serializer.data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    
                },
                # "user":   # This converts the object to JSON automatically
            }, status=status.HTTP_200_OK)

            else:
                return Response(
                    {"error": "Invalid credentials"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    from rest_framework.permissions import IsAuthenticated

# --- GET CURRENT USER ---
class CurrentUserView(APIView):
    # permission_classes = [IsAuthenticated] # Only logged-in users can access this

    def get(self, request):
        # request.user is automatically populated by the JWT token
        user = request.user
        serializer = UserTableSerializer(user)
        
        return Response({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "all_details": serializer.data
        }, status=status.HTTP_200_OK)

# --- LOGOUT (Blacklist Token) ---
class LogoutView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # The frontend should send the 'refresh' token to be blacklisted
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or already logged out."}, status=status.HTTP_400_BAD_REQUEST)