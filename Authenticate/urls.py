from django.urls import path, include
from .authView import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup', UserView.as_view()),
    path('token', UserLoginView.as_view()),
    # path('token', TokenObtainPairView.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('me', CurrentUserView.as_view(), name='current_user'),
    path('logout', LogoutView.as_view(), name='logout'),
]
