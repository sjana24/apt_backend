from django.urls import path
from .timeTable.timeTableViewByLab import *
from .timeTable.timeTableView import  *
from .course.courseView import *
from .staff.staffView import *
from .lab.labView import *
from .degree.degreeView import *
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

     # Lab timetable endpoints
    path('timetable-slots/by-lab', TimetableSlotLabViewSet.as_view({'post': 'by_lab'}), name='timetable-by-lab'),

]
