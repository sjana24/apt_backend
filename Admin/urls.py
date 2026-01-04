from django.urls import path, include
from .courseModuleView import *
from .staffView import *
from .labView import *
from .degreeView import *
from .courseXstaffView import *

urlpatterns = [
    path('course',CourseModuleView .as_view()),
    path('course/<int:pk>/', CourseModuleView.as_view()),

    path('staffs', StaffView.as_view(), name='staff-list'),
    path('staffs/<int:pk>/', StaffView.as_view(), name='staff-detail'),

    path('labs', LabView.as_view(), name='lab-list'),
    path('labs/<int:pk>/', LabView.as_view(), name='lab-detail'),

    path('degree', DegreeView.as_view(), name='degree-list'),
    path('degree/<int:pk>', DegreeView.as_view(), name='degree-detail'),
    path('degree/details/<int:degree_id>', DegreeDetailWithModulesView.as_view(), name='degree-details-modules'),

    # Main endpoint for listing and creating assignments
    path('course-staff', CourseStaffView.as_view(), name='course-staff-list'),
    
    # Endpoint for deleting a specific assignment
    path('course-staff/<int:pk>', CourseStaffView.as_view(), name='course-staff-detail'),
]
