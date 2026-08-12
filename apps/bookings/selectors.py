from django.db.models import QuerySet, Q
from .models import BookingRequest, BookingStatus
from apps.lsas.models import LSAProfile
from typing import Optional
from datetime import datetime

def get_overlapping_bookings(lsa: LSAProfile, session_start: datetime, session_end: datetime) -> QuerySet[BookingRequest]:
    """
    Returns bookings for the given LSA that overlap with the given time range.
    Overlap condition: existing_start < new_end AND existing_end > new_start
    Blocking states: PENDING, CONFIRMED
    """
    return BookingRequest.objects.filter(
        lsa=lsa,
        status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        session_start__lt=session_end,
        session_end__gt=session_start
    )
