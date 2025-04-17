from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('SELLER', 'Seller'),
        ('CONSUMER', 'Consumer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CONSUMER')

    def __str__(self):
        return f"{self.username} ({self.role})"
