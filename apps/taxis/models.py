from django.db import models
import uuid

from django.conf import settings
# Create your models here.

class Driver(models.Model):

    class StatusType(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Disponible"
        ON_A_RIDE = "ON_A_RIDE", "En course"
        UNAVAILABLE = "UNAVAILABLE", "Hors service"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid7,
        editable=False
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver"
    )

    license_number = models.CharField(
        max_length=100,
        unique=True
    )

    availability_status = models.CharField(
        max_length=30,
        choices=StatusType.choices,
        default=StatusType.UNAVAILABLE
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    location_updated_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at", "license_number"]
       

    def __str__(self):
        return f"{self.license_number} - {self.availability_status}"




    



class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid7,editable=False)
    driver = models.ForeignKey(Driver,on_delete=models.CASCADE,related_name="vehicles")
    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=255,unique=True)
    seats = models.PositiveSmallIntegerField()
    vehicle_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering =['-created_at','model']

    def __str__(self):
        return f"- {self.brand} - {self.model} - {self.registration_number}"
