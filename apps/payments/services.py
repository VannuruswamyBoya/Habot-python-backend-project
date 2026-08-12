from django.db import transaction
from apps.bookings.models import BookingRequest
from apps.payments.models import Payment, PaymentStatus
from apps.payments.razorpay_client import RazorpayClient
from decimal import Decimal

@transaction.atomic
def create_payment_for_booking(booking: BookingRequest) -> Payment:
    """
    Creates a Razorpay order and the corresponding Payment stub for a BookingRequest.
    If the Payment already exists, it returns it (or fails if it shouldn't happen).
    """
    if hasattr(booking, 'payment'):
        return booking.payment

    # Calculate amount
    duration_hours = Decimal((booking.session_end - booking.session_start).total_seconds()) / Decimal(3600)
    amount_inr = duration_hours * booking.lsa.hourly_rate
    amount_minor_units = int(amount_inr * 100)
    
    # Create Razorpay order
    rzp_client = RazorpayClient()
    order = rzp_client.create_order(
        amount=amount_minor_units,
        currency='INR',
        receipt=f"booking_{booking.id}"
    )
    
    # Create Payment
    payment = Payment.objects.create(
        booking=booking,
        razorpay_order_id=order['id'],
        amount=amount_minor_units,
        currency='INR',
        status=PaymentStatus.CREATED
    )
    
    return payment

@transaction.atomic
def verify_and_update_payment(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> Payment:
    """
    Verifies the payment and updates the Payment and BookingRequest status.
    """
    payment = Payment.objects.select_for_update().get(razorpay_order_id=razorpay_order_id)
    
    if payment.status == PaymentStatus.SUCCESS:
        # Idempotent return
        return payment

    rzp_client = RazorpayClient()
    is_valid = rzp_client.verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)
    
    if is_valid:
        payment.status = PaymentStatus.SUCCESS
        payment.razorpay_payment_id = razorpay_payment_id
        payment.signature_verified = True
        payment.save()
        
        # Update booking
        from apps.bookings.services import transition_booking_status
        from apps.bookings.models import BookingStatus
        transition_booking_status(payment.booking, BookingStatus.CONFIRMED)
    else:
        payment.status = PaymentStatus.FAILED
        payment.razorpay_payment_id = razorpay_payment_id
        payment.save()
        
        from apps.bookings.services import transition_booking_status
        from apps.bookings.models import BookingStatus
        transition_booking_status(payment.booking, BookingStatus.FAILED)
        
    return payment

@transaction.atomic
def handle_webhook_event(event: str, payload: dict):
    """
    Handles Razorpay webhook events for payment capturing and failures.
    Ensures idempotency using select_for_update and status checks.
    """
    if event not in ['payment.captured', 'payment.failed']:
        return # Ignore other events for now

    payment_entity = payload.get('payment', {}).get('entity', {})
    razorpay_order_id = payment_entity.get('order_id')
    razorpay_payment_id = payment_entity.get('id')

    if not razorpay_order_id:
        return

    try:
        payment = Payment.objects.select_for_update().get(razorpay_order_id=razorpay_order_id)
    except Payment.DoesNotExist:
        return

    # Idempotency check
    if payment.status in [PaymentStatus.SUCCESS, PaymentStatus.FAILED]:
        return

    from apps.bookings.services import transition_booking_status
    from apps.bookings.models import BookingStatus

    if event == 'payment.captured':
        payment.status = PaymentStatus.SUCCESS
        payment.razorpay_payment_id = razorpay_payment_id
        payment.signature_verified = True # Webhook signature is already verified
        payment.save()
        transition_booking_status(payment.booking, BookingStatus.CONFIRMED)
    elif event == 'payment.failed':
        payment.status = PaymentStatus.FAILED
        payment.razorpay_payment_id = razorpay_payment_id
        payment.save()
        transition_booking_status(payment.booking, BookingStatus.FAILED)
