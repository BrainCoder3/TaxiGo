from django.db import models
from django.db.models import Q
import uuid
from django.conf import settings
from apps.taxis.models import Driver
# Create your models here.
class FareGrid(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid7,editable=False)
    pickup_price = models.DecimalField(max_digits=9,decimal_places=2)
    price_per_km = models.DecimalField(max_digits=6,decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at','price_per_km']
        constraints = [
            models.UniqueConstraint(
                fields=['active'],
                condition=Q(active=True),
                name="unique_active_fare_grid"

            )
        ]

    def __str__(self):
        return f"{self.pickup_price} + {self.price_per_km}/km"


class Ride(models.Model):
    class  StatusType(models.TextChoices):
        WAITING ="WAITING","en attente"
        ACCEPTED = "ACCEPTED","acceptée"
        IN_PROGRESS = "IN_PROGRESS","en cours"
        COMPLETED = "COMPLETED","Terminée"
        CANCELLED = "CANCELLED", "annulée"
    id = models.UUIDField(primary_key=True,default=uuid.uuid7,editable=False)
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="rides")
    driver = models.ForeignKey(Driver,on_delete=models.SET_NULL,related_name='rides',blank=True,null=True)
    departure_latitude = models.DecimalField(max_digits=9,decimal_places=6)
    departure_longitude = models.DecimalField(max_digits=9,decimal_places=6)
    arrival_latitude = models.DecimalField(max_digits=9,decimal_places=6)
    arrival_longitude =models.DecimalField(max_digits=9,decimal_places=6)
    distance_km = models.DecimalField(max_digits=9,decimal_places=3)
    estimated_price = models.DecimalField(max_digits=9,decimal_places=2)
    status = models.CharField(max_length=30,choices=StatusType.choices,default=StatusType.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "status"]

        constraints = [
            models.UniqueConstraint(
                fields=["passenger"],
                condition=Q(
                    status__in=[
                        "WAITING",
                        "ACCEPTED",
                        "IN_PROGRESS",
                    ]
                ),
                name="unique_active_ride_per_passenger",
            ),

            models.UniqueConstraint(
                fields=["driver"],
                condition=Q(
                    status__in=[
                        "ACCEPTED",
                        "IN_PROGRESS",
                    ]
                ),
                name="unique_active_ride_per_driver",
            ),
        ]

    def __str__(self):
        return f"passenger:{self.passenger} - driver{self.driver}-{self.status}"