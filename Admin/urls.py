from django.urls import path, include
from .courseView import *
from .staffView import *
from .labView import *
from .degreeView import *
from .courseXstaffView import *

urlpatterns = [
    path('course',CourseModuleView .as_view()),
    path('course/<int:pk>', CourseModuleUpdateView.as_view()),
    path('course/staff/<int:staff_id>/', StaffCourseDetailsView.as_view(), name='staff-course-details'),

    path('staffs', StaffView.as_view(), name='staff-list'),
    
    path('staffs/<int:pk>', StaffView.as_view(), name='staff-assignments'),
    path('staffs/<int:pk>/', StaffView.as_view(), name='staff-detail'),

    # path('labs', LabView.as_view(), name='lab-list'),
    # path('labs/<int:pk>/', LabView.as_view(), name='lab-detail'),

    path('degree', DegreeView.as_view(), name='degree-list'),
    path('degree/<int:pk>', DegreeUpdateView.as_view(), name='degree-detail'),
    path('degree/staff/<int:staff_id>/', StaffAssignmentsByDegreeView.as_view(), name='staff-degree-assignments'),

    # Main endpoint for listing and creating assignments
    # path('course-staff', CourseStaffView.as_view(), name='course-staff-list'),
    
    # Endpoint for deleting a specific assignment
    # path('course-staff/<int:pk>', CourseStaffView.as_view(), name='course-staff-detail'),


    
    # Get a specific degree with its modules
    # path('degrees-with-modules/<int:degree_id>/', SingleDegreeModuleView.as_view(), name='degree-modules-detail'),
]
