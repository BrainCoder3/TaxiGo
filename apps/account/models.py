from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.


class User(AbstractUser):
    class RoleType(models.TextChoices) :
        CLIENT = "CLIENT", "Passager"
        DRIVER = "DRIVER", "Chauffeur"
        ADMIN = "ADMIN", "Administrateur"
    id = models.UUIDField(primary_key=True,default=uuid.uuid7,editable=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30)
    role = models.CharField(max_length=30, choices=RoleType.choices,default=RoleType.CLIENT)
    email_verified_at = models.DateTimeField(blank=True,null=True)
    phone_verified_at = models.DateTimeField(blank=True,null=True)
    last_activity_at = models.DateTimeField(blank=True,null=True)


    USERNAME_FIELD ='email'
    REQUIRED_FIELDS=["username"]

    def __str__(self):
        return f"{self.username} - {self.email}"
    
