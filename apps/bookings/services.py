from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import BookingRequest, BookingStatus
from apps.parents.models import Parent
from apps.lsas.models import LSAProfile
from apps.payments.models import Payment, PaymentStatus
from .exceptions import BookingConflictException, InvalidBookingDataException
from .selectors import get_overlapping_bookings

@transaction.atomic
def create_booking(parent: Parent, lsa: LSAProfile, session_start: datetime, session_end: datetime) -> BookingRequest:
    # Basic validation
    if not lsa.is_active:
        raise InvalidBookingDataException("The selected LSA is not active.")
    
    if session_start >= session_end:
        raise InvalidBookingDataException("Session start time must be before session end time.")
        
    if session_start < timezone.now():
        raise InvalidBookingDataException("Session cannot be scheduled in the past.")

    # Concurrency control: lock the LSA row to prevent race conditions during availability check
    # We use select_for_update() to serialize booking requests for the same LSA
    _ = LSAProfile.objects.select_for_update().get(id=lsa.id)

    # Check for overlaps
    overlapping = get_overlapping_bookings(lsa, session_start, session_end)
    if overlapping.exists():
        raise BookingConflictException("The LSA is already booked during the requested time.")

    # Calculate duration and amount
    duration_hours = Decimal((session_end - session_start).total_seconds()) / Decimal(3600)
    amount_inr = duration_hours * lsa.hourly_rate
    amount_minor_units = int(amount_inr * 100)  # Paise

    # Create Booking
    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        session_start=session_start,
        session_end=session_end,
        status=BookingStatus.PENDING
    )

    # Create Payment via Payment Service
    from apps.payments.services import create_payment_for_booking
    payment = create_payment_for_booking(booking)
    booking.payment = payment

    return booking

@transaction.atomic
def transition_booking_status(booking: BookingRequest, new_status: str):
    """
    State transitions for booking
    """
    valid_transitions = {
        BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.FAILED, BookingStatus.CANCELLED],
        BookingStatus.CONFIRMED: [BookingStatus.CANCELLED],
    }
    
    if new_status not in valid_transitions.get(booking.status, []):
        raise InvalidBookingDataException(f"Invalid transition from {booking.status} to {new_status}")
        
    booking.status = new_status
    booking.save(update_fields=['status', 'updated_at'])
    return booking
