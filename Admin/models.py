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
    capacity = models.PositiveIntegerField() # Number of students the lab can hold
    availability = models.BooleanField(default=True)
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'labs'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"
    

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