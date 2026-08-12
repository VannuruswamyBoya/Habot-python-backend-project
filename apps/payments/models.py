from django.db import models
from common.models import TimeStampedModel
from apps.bookings.models import BookingRequest

class PaymentStatus(models.TextChoices):
    CREATED = 'CREATED', 'Created'
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'

class Payment(TimeStampedModel):
    booking = models.OneToOneField(BookingRequest, on_delete=models.PROTECT, related_name='payment')
    razorpay_order_id = models.CharField(max_length=100, unique=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    amount = models.IntegerField(help_text="Amount in minor units (e.g., paise for INR)")
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.CREATED,
        db_index=True
    )
    signature_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for {self.booking.id} - {self.status}"
