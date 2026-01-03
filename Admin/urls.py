from django.urls import path, include
from .courseModuleView import *
from .staffView import *
from .labView import *

urlpatterns = [
    path('course',CourseModuleView .as_view()),
    path('course/<int:pk>/', CourseModuleView.as_view()),

    path('staffs', StaffView.as_view(), name='staff-list'),
    path('staffs/<int:pk>/', StaffView.as_view(), name='staff-detail'),

    path('labs', LabView.as_view(), name='lab-list'),
    path('labs/<int:pk>/', LabView.as_view(), name='lab-detail'),
]
