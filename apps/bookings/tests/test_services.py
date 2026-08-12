from django.test import TestCase
from datetime import timedelta
from django.utils import timezone
from apps.parents.models import Parent
from apps.lsas.models import LSAProfile
from apps.bookings.models import BookingRequest, BookingStatus
from apps.bookings.services import create_booking, transition_booking_status
from apps.bookings.exceptions import BookingConflictException, InvalidBookingDataException
from decimal import Decimal
from unittest.mock import patch
import apps.payments.services

class BookingServiceTests(TestCase):

    def setUp(self):
        self.parent = Parent.objects.create(name="Test Parent", email="parent@example.com")
        self.lsa = LSAProfile.objects.create(
            name="Test LSA", 
            email="lsa@example.com",
            hourly_rate=Decimal("1000.00"),
            is_active=True
        )
        
        # Mock Razorpay
        self.patcher = patch('apps.payments.services.RazorpayClient')
        self.mock_client = self.patcher.start()
        self.mock_client.return_value.create_order.return_value = {'id': 'order_mock123'}

    def tearDown(self):
        self.patcher.stop()

    def test_create_booking_success(self):

        now = timezone.now()
        start = now + timedelta(days=1, hours=10)
        end = start + timedelta(hours=1)
        
        booking = create_booking(self.parent, self.lsa, start, end)
        
        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.status, BookingStatus.PENDING)
        self.assertIsNotNone(booking.payment)
        self.assertEqual(booking.payment.amount, 100000)  # 1000.00 * 100 paise

    def test_create_booking_inactive_lsa(self):
        self.lsa.is_active = False
        self.lsa.save()
        
        now = timezone.now()
        start = now + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        with self.assertRaises(InvalidBookingDataException):
            create_booking(self.parent, self.lsa, start, end)

    def test_create_booking_past_date(self):
        now = timezone.now()
        start = now - timedelta(days=1)
        end = start + timedelta(hours=1)
        
        with self.assertRaises(InvalidBookingDataException):
            create_booking(self.parent, self.lsa, start, end)

    def test_create_booking_conflict(self):
        now = timezone.now()
        start = now + timedelta(days=1, hours=10)
        end = start + timedelta(hours=1)
        
        # First booking
        create_booking(self.parent, self.lsa, start, end)
        
        # Overlapping booking (starts half an hour later)
        start2 = start + timedelta(minutes=30)
        end2 = start2 + timedelta(hours=1)
        
        with self.assertRaises(BookingConflictException):
            create_booking(self.parent, self.lsa, start2, end2)

    def test_transition_booking_status(self):
        now = timezone.now()
        start = now + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        booking = create_booking(self.parent, self.lsa, start, end)
        self.assertEqual(booking.status, BookingStatus.PENDING)
        
        transition_booking_status(booking, BookingStatus.CONFIRMED)
        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingStatus.CONFIRMED)
        
        with self.assertRaises(InvalidBookingDataException):
            transition_booking_status(booking, BookingStatus.PENDING)
