from django.urls import path, include
from .timeTableViewByLab import *
from .timeTableView import  *
# from Admin.timeTableViewByLab import TimetableSlotLabListCreateAPIView
from .courseView import *
from .staffView import *
from .labView import *
from .degreeView import *
from .courseXstaffView import *

urlpatterns = [
    path('course',CourseModuleView .as_view()),
    path('course/<int:pk>', CourseModuleUpdateView.as_view()),
    path('course/staff/<int:staff_id>', StaffCourseDetailsView.as_view(), name='staff-course-details'),

    path('staff', StaffView.as_view(), name='staff-list'),    
    path('staff/<int:pk>', StaffView.as_view(), name='staff-assignments'),
    path('staff/<int:pk>', StaffView.as_view(), name='staff-detail'),

    path('labs', LabView.as_view(), name='lab-list'),
    path('labs/staff', LabViewStaff.as_view(), name='lab-list'),
    path('labs/<int:pk>', LabView.as_view(), name='lab-detail'),
    path('labs/availability/<int:pk>', LabView.as_view(), name='lab-detail'),

     # New availability endpoint (keeps your existing pattern)
    path('labs/availability/<int:pk>/', LabAvailabilityView.as_view(), name='lab-availability-detail'),
    path('labs/check-availability', LabAvailabilityView.as_view(), name='lab-availability-list'),
    

    path('degree', DegreeView.as_view(), name='degree-list'),
    path('degreeSearch', DegreeSearchView.as_view(), name='degree-searchlist'),
    path('degree/<int:pk>', DegreeUpdateView.as_view(), name='degree-detail'),
    path('degree/staff/<int:staff_id>/', StaffAssignmentsByDegreeView.as_view(), name='staff-degree-assignments'),

    path('timetable-slots', TimetableSlotListCreateAPIView.as_view(), name='timetable-slot-list-create'),
    path('timetable-slots/<int:pk>', TimetableSlotDetailAPIView.as_view(), name='timetable-slot-detail'),
     # Additional custom endpoints
    path('timetable/by-degree', TimetableSlotViewSet.as_view({'get': 'list'}), name='timetable-by-degree'),
    path('timetable/check-availability', TimetableSlotViewSet.as_view({'get': 'check_availability'}), name='check-availability'),

    # Main endpoint for listing and creating assignments
    # path('course-staff', CourseStaffView.as_view(), name='course-staff-list'),
    
    # Endpoint for deleting a specific assignment
    # path('course-staff/<int:pk>', CourseStaffView.as_view(), name='course-staff-detail'),

     # Lab timetable endpoints
    path('timetable-slots/by-lab', TimetableSlotLabViewSet.as_view({'post': 'by_lab'}), name='timetable-by-lab'),
    # path('timetable-slots/by-lab/available/', TimetableSlotLabListCreateAPIView.as_view({'post': 'by_lab_available_only'}), name='timetable-by-lab-available'),
    # path('timetable-slots/by-lab/booked/', TimetableSlotLabListCreateAPIView.as_view({'post': 'by_lab_booked_only'}), name='timetable-by-lab-booked'),
    # path('timetable-slots/check-slot/', TimetableSlotLabListCreateAPIView.as_view({'post': 'check_slot_availability'}), name='check-slot-availability'),
    # path('timetable-slots/by-lab/daily-summary/', TimetableSlotLabListCreateAPIView.as_view({'post': 'daily_summary_by_lab'}), name='daily-summary-by-lab'),
    
    # Individual slot operations
    # path('timetable-slots/<int:pk>/', TimetableSlotDetailAPIView.as_view(), name='timetable-slot-detail'),

    
    # Get a specific degree with its modules
    # path('degrees-with-modules/<int:degree_id>/', SingleDegreeModuleView.as_view(), name='degree-modules-detail'),
]
