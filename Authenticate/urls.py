from django.urls import path
from .authView import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup', UserView.as_view()),
    path('token', UserLoginView.as_view()),
    # path('token', TokenObtainPairView.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('me', CurrentUserView.as_view(), name='current_user'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('change-password', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password', ResetPasswordView.as_view(), name='reset_password'),
]
