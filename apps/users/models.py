from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('librarian', 'Librarian'),
        ('staff', 'Staff'),
        ('member', 'Member'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    phone_number = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_librarian(self):
        return self.role in ['admin', 'librarian']
    
    @property
    def is_staff_role(self):
        return self.role in ['admin', 'librarian', 'staff']
