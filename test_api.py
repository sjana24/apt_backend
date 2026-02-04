import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from Authenticate.models import UserTable
from Admin.models import CourseStaff
from Admin.serializers.staff import StaffModuleDetailSerializer

# Get staff member
staff = UserTable.objects.filter(email='sarah.johnson@uwu.ac.lk').first()
print(f"Testing API for Staff ID: {staff.id} - {staff.full_name}\n")

# Simulate what the API endpoint does
assignments = CourseStaff.objects.filter(staff_id=staff.id).select_related(
    'course_module',
    'course_module__degree',
)

print(f"Found {assignments.count()} assignments")

if assignments.exists():
    serializer = StaffModuleDetailSerializer(assignments, many=True)
    print("\nSerialized data (first 3):")
    for item in serializer.data[:3]:
        print(f"  {item}")
else:
    print("No assignments found!")
