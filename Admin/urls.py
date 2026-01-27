from django.urls import path
from .degree.degreeViewSet import DegreeViewSet
from .course.courseViewSet import CourseModuleViewSet, StaffCourseDetailsView
from .staff.staffViewSet import StaffViewSet
from .lab.labViewSet import LabViewSet
from .lab.labView import LabAvailabilityView
from .timeTable.timeTableViewByLab import TimetableSlotLabViewSet
from .timeTable.timeTableView import TimetableSlotListCreateAPIView, TimetableSlotDetailAPIView, TimetableSlotViewSet
from .courseXstaffView import StaffAssignmentsByDegreeView
from .assignment.assignmentViewSet import AssignmentViewSet

urlpatterns = [
    # --- ASSIGNMENT ENDPOINTS ---
    path('assignments', AssignmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='assignment-list'),
    path('assignments/<int:pk>', AssignmentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='assignment-detail'),

    # --- COURSE ENDPOINTS ---
    path('course', CourseModuleViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('course/<int:pk>', CourseModuleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('course/staff/<int:staff_id>', StaffCourseDetailsView.as_view(), name='staff-course-details'),

    # --- STAFF ENDPOINTS ---
    path('staff', StaffViewSet.as_view({'get': 'list'})),    
    # NOTE: Original had duplicates for staff/<int:pk>, unifying them
    path('staff/<int:pk>', StaffViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='staff-detail'),

    # --- LAB ENDPOINTS ---
    path('labs', LabViewSet.as_view({'get': 'list', 'post': 'create'}), name='lab-list'),
    path('labs/staff', LabViewSet.as_view({'get': 'available_labs'}), name='lab-list-staff'),
    path('labs/<int:pk>', LabViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='lab-detail'),
    # Note: 'labs/availability/<int:pk>' was duplicate in original pointing to LabView. Mapping to retrieve.
    path('labs/availability/<int:pk>', LabViewSet.as_view({'get': 'retrieve'}), name='lab-detail-avail'),

    # Availability Logic (Complex custom views kept as is)
    path('labs/availability/<int:pk>/', LabAvailabilityView.as_view(), name='lab-availability-detail'),
    path('labs/check-availability', LabAvailabilityView.as_view(), name='lab-availability-list'),
    
    # --- DEGREE ENDPOINTS ---
    path('degree', DegreeViewSet.as_view({'get': 'list', 'post': 'create'}), name='degree-list'),
    path('degreeSearch', DegreeViewSet.as_view({'get': 'search'}), name='degree-searchlist'),
    path('degree/<int:pk>', DegreeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='degree-detail'),
    path('degree/staff/<int:staff_id>/', StaffAssignmentsByDegreeView.as_view(), name='staff-degree-assignments'),

    # --- TIMETABLE ENDPOINTS ---
    path('timetable-slots', TimetableSlotListCreateAPIView.as_view(), name='timetable-slot-list-create'),
    path('timetable-slots/<int:pk>', TimetableSlotDetailAPIView.as_view(), name='timetable-slot-detail'),
    
    # Custom Timetable Logic
    path('timetable/by-degree', TimetableSlotViewSet.as_view({'get': 'list'}), name='timetable-by-degree'),
    path('timetable/dashboard-stats', TimetableSlotViewSet.as_view({'get': 'dashboard_stats'}), name='dashboard-stats'),
    path('timetable/my-schedule', TimetableSlotViewSet.as_view({'get': 'my_schedule'}), name='my-schedule'),
    path('timetable-slots/by-lab', TimetableSlotLabViewSet.as_view({'post': 'by_lab'}), name='timetable-by-lab'),
]
