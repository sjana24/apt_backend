from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.contrib.auth import authenticate,login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import secrets
import re

class UserView(APIView):
    def post(self, request):
        # 1. Extract data from the request
        data = request.data
        email = data.get('email', '').strip()
        full_name = data.get('name', '').strip()
        password = data.get('password')
        role = data.get('role', 'staff') # Default to staff if not provided

        # 2. Basic Validation
        if not email or not password or not full_name:
            return Response(
                {"error": "Email, full_name, and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Email Validation
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"error": "Invalid email format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 4. Email domain validation (optional - prevent disposable emails)
        email_lower = email.lower()
        blocked_domains = ['tempmail.com', 'throwaway.email', '10minutemail.com']
        if any(domain in email_lower for domain in blocked_domains):
            return Response(
                {"error": "Email from disposable email services is not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 5. Check if email already exists
        if UserTable.objects.filter(email=email).exists():
            return Response(
                {"error": "An account with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 6. Password strength validation
        if len(password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for at least one letter and one number
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            return Response(
                {"error": "Password must contain both letters and numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 7. Use the Manager to create the user
            # This triggers UserTableManager.create_user()
            user = UserTable.objects.create_user(
                email=email.lower(),  # Store email in lowercase
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
        userEmail = data.get('email', '').strip()
        userPassword = data.get('password')

        if not userEmail or not userPassword :
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Email format validation
        try:
            validate_email(userEmail)
        except ValidationError:
            return Response(
                {"error": "Invalid email format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:

            # user_verification =authenticate(ëmail = userEmail ,password = userPassword)
            user = authenticate(request, email=userEmail.lower(), password=userPassword)
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
    permission_classes = [IsAuthenticated] # Only logged-in users can access this

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # The frontend should send the 'refresh' token to be blacklisted
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or already logged out."}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "Old and new passwords are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({"error": "Incorrect old password."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Password strength validation
        if len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password):
            return Response(
                {"error": "Password must contain both letters and numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if new password is same as old password
        if user.check_password(new_password):
            return Response(
                {"error": "New password must be different from old password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user.set_password(new_password)
            user.save()
            
            # Generate new tokens for the user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Password changed successfully.",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# --- FORGOT PASSWORD (Request Reset) ---
class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip()
        
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Email format validation
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserTable.objects.get(email=email.lower())
            
            # Generate a 6-digit OTP
            reset_otp = str(secrets.randbelow(900000) + 100000)
            
            # Set OTP expiry (10 minutes from now)
            user.reset_otp = reset_otp
            user.reset_otp_expiry = timezone.now() + timedelta(minutes=10)
            user.save()
            
            # Send OTP via email
            send_mail(
                subject="Password Reset OTP",
                message=f"Hello {user.full_name},\n\nYour password reset OTP is: {reset_otp}\n\nThis OTP will expire in 10 minutes.\n\nIf you didn't request this, please ignore this email and your account will remain secure.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                "message": "Password reset OTP sent successfully. Check your inbox.",
                "email": email
            }, status=status.HTTP_200_OK)
            
        except UserTable.DoesNotExist:
            # Don't reveal whether the user exists or not (security best practice)
            return Response({
                "message": "If an account exists with this email, a password reset link has been sent."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- VERIFY OTP ---
class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip()
        otp = request.data.get("otp", "").strip()
        
        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserTable.objects.get(email=email.lower())
            
            # Check if OTP matches
            if user.reset_otp != otp:
                return Response({"error": "Invalid OTP. Please check and try again."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if OTP has expired
            if user.reset_otp_expiry < timezone.now():
                return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"message": "OTP verified successfully. You can now reset your password."}, status=status.HTTP_200_OK)
            
        except UserTable.DoesNotExist:
            return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# --- RESET PASSWORD (After OTP Verification) ---
class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip()
        otp = request.data.get("otp", "").strip()
        new_password = request.data.get("new_password")
        
        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Password strength validation
        if len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password):
            return Response(
                {"error": "Password must contain both letters and numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = UserTable.objects.get(email=email.lower())
            
            # Verify OTP again
            if user.reset_otp != otp:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if OTP has expired
            if user.reset_otp_expiry < timezone.now():
                return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update password
            user.set_password(new_password)
            user.reset_otp = None  # Clear the OTP
            user.reset_otp_expiry = None
            user.save()
            
            return Response({"message": "Password reset successfully. You can now login with your new password."}, status=status.HTTP_200_OK)
            
        except UserTable.DoesNotExist:
            return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)