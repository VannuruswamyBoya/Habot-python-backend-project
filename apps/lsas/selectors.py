from django.db.models import QuerySet, Exists, OuterRef
from apps.lsas.models import LSAProfile
from apps.bookings.models import BookingRequest, BookingStatus
from typing import Optional
from datetime import datetime

def search_lsas(
    skill: Optional[str] = None,
    session_start: Optional[datetime] = None,
    session_end: Optional[datetime] = None
) -> QuerySet[LSAProfile]:
    """
    Search for active LSAs filtered by skill and availability.
    Uses Exists to prevent N+1 query problems.
    """
    queryset = LSAProfile.objects.filter(is_active=True)

    if skill:
        queryset = queryset.filter(skills__contains=[skill])

    if session_start and session_end:
        # We want LSAs that DO NOT have an overlapping booking
        overlapping_bookings = BookingRequest.objects.filter(
            lsa=OuterRef('pk'),
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            session_start__lt=session_end,
            session_end__gt=session_start
        )
        queryset = queryset.annotate(
            has_overlap=Exists(overlapping_bookings)
        ).filter(has_overlap=False)

    return queryset
