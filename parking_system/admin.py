from django.contrib import admin
from .models import ParkingSlot, Booking


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ['slot_name', 'is_available']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'user_name',
        'phone_number',
        'vehicle_number',
        'vehicle_type',
        'slot',
        'booking_time'
    ]