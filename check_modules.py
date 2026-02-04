import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from Admin.models import CourseModule, CourseStaff
from Authenticate.models import UserTable

print(f'Total modules: {CourseModule.objects.count()}')
print(f'Modules with degree: {CourseModule.objects.filter(degree__isnull=False).count()}')
print(f'Modules without degree: {CourseModule.objects.filter(degree__isnull=True).count()}')

staff = UserTable.objects.filter(email='sarah.johnson@uwu.ac.lk').first()
if staff:
    print(f'\nStaff ID: {staff.id}')
    print(f'Staff: {staff.full_name}')
    
    assignments = CourseStaff.objects.filter(staff=staff).select_related('course_module__degree')
    print(f'Total assignments: {assignments.count()}')
    
    print('\nFirst 5 modules:')
    for a in assignments[:5]:
        degree_info = f"{a.course_module.degree.degreeProgram} L{a.course_module.degree.level}" if a.course_module.degree else "No degree"
        print(f"  - {a.course_module.module_code}: {a.course_module.module_name} | {degree_info}")
