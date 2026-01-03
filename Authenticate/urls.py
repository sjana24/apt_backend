from django.urls import path, include
from .authView import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup', UserView.as_view()),
    path('login', UserLoginView.as_view()),
    path('token', TokenObtainPairView.as_view()),
    path('refresh', TokenRefreshView.as_view()),
]
