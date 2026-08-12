from django.db import models
from common.models import TimeStampedModel
from apps.parents.models import Parent
from apps.lsas.models import LSAProfile

class BookingStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    FAILED = 'FAILED', 'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class BookingRequest(TimeStampedModel):
    parent = models.ForeignKey(Parent, on_delete=models.PROTECT, related_name='bookings')
    lsa = models.ForeignKey(LSAProfile, on_delete=models.PROTECT, related_name='bookings')
    session_start = models.DateTimeField(db_index=True)
    session_end = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        db_index=True
    )

    class Meta:
        ordering = ['-session_start']
        indexes = [
            models.Index(fields=['lsa', 'session_start', 'session_end']),
        ]

    def __str__(self):
        return f"Booking {self.id} for {self.lsa.name} by {self.parent.name}"
