from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.utils import timezone

from django.core.mail import send_mail

from .models import (
    ParkingSlot,
    Booking
)

import qrcode

from io import BytesIO

from django.core.files import File


# =========================
# Home Page
# =========================

def home(request):

    filter_type = request.GET.get('filter')

    if filter_type == 'available':

        slots = ParkingSlot.objects.filter(
            is_available=True
        )

    elif filter_type == 'occupied':

        slots = ParkingSlot.objects.filter(
            is_available=False
        )

    else:

        slots = ParkingSlot.objects.all()

    bookings = Booking.objects.all()

    # AI Recommended Slot
    recommended_slot = ParkingSlot.objects.filter(
        is_available=True
    ).first()

    total_slots = ParkingSlot.objects.count()

    available_slots = ParkingSlot.objects.filter(
        is_available=True
    ).count()

    occupied_slots = ParkingSlot.objects.filter(
        is_available=False
    ).count()

    context = {

        'slots': slots,

        'bookings': bookings,

        'recommended_slot': recommended_slot,

        'total_slots': total_slots,

        'available_slots': available_slots,

        'occupied_slots': occupied_slots,

    }

    return render(
        request,
        'home.html',
        context
    )


# =========================
# Dashboard Page
# =========================

def dashboard(request, slot_id):

    slot = get_object_or_404(
        ParkingSlot,
        id=slot_id
    )

    if request.method == "POST":

        request.session['user_name'] = request.POST.get(
            'user_name'
        )

        request.session['phone_number'] = request.POST.get(
            'phone_number'
        )

        request.session['vehicle_number'] = request.POST.get(
            'vehicle_number'
        )

        request.session['vehicle_type'] = request.POST.get(
            'vehicle_type'
        )

        request.session['email'] = request.POST.get(
            'email'
        )

        return redirect(
            'book_slot',
            slot_id=slot.id
        )

    return render(
        request,
        'dashboard.html',
        {'slot': slot}
    )


# =========================
# Book Slot
# =========================

def book_slot(request, slot_id):

    slot = get_object_or_404(
        ParkingSlot,
        id=slot_id
    )

    vehicle_number = request.session.get(
        'vehicle_number'
    )

    # Prevent duplicate active booking

    existing_booking = Booking.objects.filter(
        vehicle_number=vehicle_number,
        exit_time__isnull=True
    ).exists()

    if existing_booking:

        return render(
            request,
            'already_booked.html'
        )

    # Prevent booking occupied slot

    if not slot.is_available:

        return redirect('home')

    # Create booking

    booking = Booking.objects.create(

        slot=slot,

        user_name=request.session.get(
            'user_name'
        ),

        phone_number=request.session.get(
            'phone_number'
        ),

        vehicle_number=vehicle_number,

        vehicle_type=request.session.get(
            'vehicle_type'
        ),

        booking_time=timezone.now()

    )

    # Generate QR Code

    qr_data = f'''
User : {booking.user_name}
Slot : {slot.slot_name}
Vehicle : {booking.vehicle_number}
'''

    qr_image = qrcode.make(qr_data)

    buffer = BytesIO()

    qr_image.save(buffer, format='PNG')

    file_name = f'booking_{booking.id}.png'

    booking.qr_code.save(
        file_name,
        File(buffer),
        save=True
    )

    # Send Email

    send_mail(

        'Parking Slot Booked Successfully 🚗',

        f'''

Hello {booking.user_name},

Your parking slot has been booked successfully.

Slot Number : {slot.slot_name}

Vehicle Number : {booking.vehicle_number}

Thank you for using AI Smart Parking Finder.

''',

        'yourgmail@gmail.com',

        [request.session.get('email')],

        fail_silently=False

    )

    # Make slot occupied

    slot.is_available = False

    slot.save()

    context = {

        'booking': booking,

        'slot': slot

    }

    return render(
        request,
        'success.html',
        context
    )


# =========================
# Cancel Booking
# =========================

def cancel_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if request.method == "POST":

        entered_name = request.POST.get(
            'user_name'
        )

        # Username verification

        if entered_name != booking.user_name:

            return render(
                request,
                'access_denied.html'
            )

        # Exit time

        exit_time = timezone.now()

        # Parking duration

        duration = exit_time - booking.booking_time

        total_hours = duration.total_seconds() / 3600

        # Parking amount calculation

        if total_hours <= 1:

            amount = 20

        else:

            extra_hours = int(total_hours - 1)

            amount = 20 + (extra_hours * 10)

        # Save exit time and amount

        booking.exit_time = exit_time

        booking.total_amount = amount

        booking.save()

        # Free the slot

        booking.slot.is_available = True

        booking.slot.save()

        context = {

            'booking': booking,

            'duration': duration,

            'amount': amount

        }

        return render(
            request,
            'bill.html',
            context
        )

    return redirect('home')


# =========================
# My Bookings
# =========================

def my_bookings(request):

    user_name = request.session.get(
        'user_name'
    )

    bookings = Booking.objects.filter(

        user_name=user_name,

        exit_time__isnull=True

    )

    return render(

        request,

        'my_bookings.html',

        {

            'bookings': bookings

        }

    )


# =========================
# Admin Login
# =========================

def admin_login(request):

    if request.method == "POST":

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        if username == "admin" and password == "admin123":

            request.session['is_admin'] = True

            return redirect('admin_dashboard')

    return render(
        request,
        'admin_login.html'
    )


# =========================
# Admin Dashboard
# =========================

def admin_dashboard(request):

    if not request.session.get(
        'is_admin'
    ):

        return redirect('admin_login')

    slots = ParkingSlot.objects.all()

    bookings = Booking.objects.all()

    context = {

        'slots': slots,

        'bookings': bookings,

    }

    return render(
        request,
        'admin_dashboard.html',
        context
    )

# =========================
# Booking History
# =========================

def booking_history(request):

    bookings = Booking.objects.all().order_by(
        '-booking_time'
    )

    context = {

        'bookings': bookings

    }

    return render(
        request,
        'history.html',
        context
    )