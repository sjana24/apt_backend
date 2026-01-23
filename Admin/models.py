from django.db import models
from datetime import datetime
from Authenticate.models import UserTable # Importing your Staff model

class Degree(models.Model):
    # Choices for Level and Semester to ensure data consistency
    LEVEL_CHOICES = [
        ('100', '100'),
        ('200', '200'),
        ('300', '300'),
        ('400', '400'),
    ]
    
    SEMESTER_CHOICES = [
        ('I', 'Semester I'),
        ('II', 'Semester II'),
    ]

    degreeProgram = models.CharField(max_length=255) # e.g., "BSc in Computer Science"
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES)
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)
    
    # Defaults to the current year (e.g., 2026)
    academicYear = models.IntegerField(default=datetime.now().year)

    def __str__(self):
        return f"{self.degreeProgram} - Year {self.level} Sem {self.semester}"

class CourseModule(models.Model):
    module_name = models.CharField(max_length=255)
    module_code = models.CharField(max_length=20, unique=True)
    credit = models.PositiveIntegerField() # Using PositiveInt for credit hours/points
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='modules',null=True, blank=True )
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_modules'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.module_code} - {self.module_name}"
    
class Lab(models.Model):
    name = models.CharField(max_length=100, unique=True)
    lab_code = models.CharField(
        max_length=20,
        default="NEW"
    )
    capacity = models.PositiveIntegerField()
    availability = models.BooleanField(default=True)

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'labs'
        ordering = ['name']

    def __str__(self):
        return f"{self.lab_code} - {self.name} (Cap: {self.capacity})"

    

class CourseStaff(models.Model):
    # Link to the Module
    course_module = models.ForeignKey(
        'CourseModule', 
        on_delete=models.CASCADE, 
        related_name='staff_assignments'
    )
    
    # Link to the Staff member (UserTable)
    staff = models.ForeignKey(
        UserTable, 
        on_delete=models.CASCADE, 
        related_name='module_assignments'
    )
    
    # Additional Info
    role = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Lead Lecturer, Lab Assistant")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents assigning the same staff to the same module multiple times
        unique_together = ('course_module', 'staff')

    def __str__(self):
        return f"{self.staff.full_name} -> {self.course_module.module_name}"
    
from django.conf import settings # Needed to reference the User model for audit

class TimetableSlot(models.Model):
    DAY_CHOICES = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
    ]

    # --- Relationships ---
    # Links to the Degree Program
    degree = models.ForeignKey(
        'Degree', 
        on_delete=models.CASCADE, 
        related_name='timetable_slots'
    )
    # Links to the Module (Optional for notes like 'Break' or 'Library')
    module = models.ForeignKey(
        'CourseModule', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='timetable_slots'
    )
    # Links to the specific Lab
    lab = models.ForeignKey(
        'Lab', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='timetable_slots'
    )

    # --- Slot Information ---
    slot_date = models.DateField(help_text="The specific calendar date for this session")
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    time_range = models.CharField(max_length=50, help_text="e.g., 08:00 - 09:00")
    note = models.CharField(max_length=255, blank=True, null=True, help_text="Extra info or activity name")

    # --- Audit Fields ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='allocated_slots'
    )

    class Meta:
        db_table = 'timetable_slots'
        # Ensures a degree doesn't have two sessions booked at the same time on the same date
        unique_together = ('degree', 'slot_date', 'time_range')
        ordering = ['slot_date', 'time_range']

    def __str__(self):
        return f"{self.slot_date} ({self.time_range}) - {self.degree.degreeProgram}"
    
