from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserTableManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, role='staff'):
        if not email:
            raise ValueError("Users must have an email address")
        
        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            role=role,
        )
        user.set_password(password) # This is where hashing happens!
        user.save(using=self._db)
        return user

class UserTable(AbstractBaseUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    
    # Audit Fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserTableManager()

    USERNAME_FIELD = 'email'  # You will log in with email
    REQUIRED_FIELDS = ['full_name'] # Fields required when creating via console

    def __str__(self):
        return f"{self.full_name} ({self.role})"