from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Employee', 'Employee'),
        ('Manager', 'Manager'),
        ('Admin', 'Admin'), # Optional: for superusers
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')

    def is_manager(self):
        return self.role == 'Manager'
    
    def is_employee(self):
        return self.role == 'Employee'
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

