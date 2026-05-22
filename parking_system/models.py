from django.db import models


class ParkingSlot(models.Model):

    slot_name = models.CharField(max_length=20)

    is_available = models.BooleanField(default=True)

    def __str__(self):

        return self.slot_name


class Booking(models.Model):

    VEHICLE_CHOICES = [

        ('Car', 'Car'),

        ('Bike', 'Bike'),

        ('EV', 'EV'),

    ]

    slot = models.ForeignKey(
        ParkingSlot,
        on_delete=models.CASCADE
    )

    user_name = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=15)

    vehicle_number = models.CharField(max_length=20)

    vehicle_type = models.CharField(
        max_length=10,
        choices=VEHICLE_CHOICES
    )

    qr_code = models.ImageField(
      upload_to='qr_codes/',
      blank=True,
      null=True
  )

    booking_time = models.DateTimeField(
        auto_now_add=True
    )

    exit_time = models.DateTimeField(
        null=True,
        blank=True
   )
 
    total_amount = models.IntegerField(
       default=0
    )

    def __str__(self):

        return f"{self.user_name} - {self.slot.slot_name}"