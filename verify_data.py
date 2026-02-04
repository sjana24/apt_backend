from Admin.models import TimetableSlot, CourseStaff, CourseModule, Degree
from Authenticate.models import UserTable

print("\n=== DATABASE VERIFICATION ===\n")

print(f"✓ Total Timetable Slots: {TimetableSlot.objects.count()}")
print(f"✓ Total Course Modules: {CourseModule.objects.count()}")
print(f"✓ Total Staff Assignments: {CourseStaff.objects.count()}")
print(f"✓ Total Degrees: {Degree.objects.count()}")
print(f"✓ Total Staff Members: {UserTable.objects.filter(role='staff').count()}")

print("\n=== SAMPLE STAFF DETAILS ===\n")
staff = UserTable.objects.filter(role='staff').first()
if staff:
    print(f"Staff Name: {staff.full_name}")
    print(f"Email: {staff.email}")
    assignments = CourseStaff.objects.filter(staff=staff)
    print(f"Modules assigned: {assignments.count()}")
    
    if assignments.exists():
        print("\nAssigned Modules:")
        for assignment in assignments[:5]:
            print(f"  - {assignment.course_module.module_code}: {assignment.course_module.module_name} ({assignment.role})")
    
    # Check timetable slots for this staff's modules
    module_ids = assignments.values_list('course_module_id', flat=True)
    slots = TimetableSlot.objects.filter(module_id__in=module_ids)
    print(f"\nTimetable slots for their modules: {slots.count()}")
    
    if slots.exists():
        print("\nSample Timetable Slots:")
        for slot in slots[:5]:
            print(f"  - {slot.slot_date} {slot.time_range}: {slot.module.module_code} in {slot.lab.lab_code}")

print("\n=== TIMETABLE DISTRIBUTION ===\n")
from datetime import datetime, timedelta
today = datetime.now().date()
this_week = TimetableSlot.objects.filter(slot_date__gte=today, slot_date__lt=today + timedelta(days=7)).count()
next_week = TimetableSlot.objects.filter(slot_date__gte=today + timedelta(days=7), slot_date__lt=today + timedelta(days=14)).count()

print(f"This week: {this_week} slots")
print(f"Next week: {next_week} slots")

print("\n=== VERIFICATION COMPLETE ===\n")
