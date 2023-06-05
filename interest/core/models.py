from django.db import models
from django.contrib.auth.models import AbstractUser

class Interest(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', "Male"),
        ('F', "Female"),
        ('O', "Others"),
    ]
    email = models.EmailField(max_length=64, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    country = models.CharField(max_length=64)
    interests = models.ManyToManyField(Interest)