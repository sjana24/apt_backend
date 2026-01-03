from django.db import models

class CourseModule(models.Model):
    module_name = models.CharField(max_length=255)
    module_code = models.CharField(max_length=20, unique=True)
    credit = models.PositiveIntegerField() # Using PositiveInt for credit hours/points
    
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
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'labs'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"