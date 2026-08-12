from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from apps.parents.models import Parent
from apps.lsas.models import LSAProfile
from apps.bookings.models import BookingRequest, BookingStatus
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth.models import User
import apps.payments.services

class BookingViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        
        self.parent = Parent.objects.create(name="Test Parent", email="parent@example.com")
        self.lsa = LSAProfile.objects.create(
            name="Test LSA", 
            email="lsa@example.com",
            hourly_rate=Decimal("1000.00"),
            is_active=True
        )
        self.url = reverse('booking-create')
        
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
        
        data = {
            "parent_id": self.parent.id,
            "lsa_id": self.lsa.id,
            "session_start": start.isoformat(),
            "session_end": end.isoformat()
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['status'], BookingStatus.PENDING)

    def test_create_booking_conflict(self):
        now = timezone.now()
        start = now + timedelta(days=1, hours=10)
        end = start + timedelta(hours=1)
        
        # Create first booking directly
        from apps.bookings.services import create_booking
        create_booking(self.parent, self.lsa, start, end)
        
        # Attempt to create conflicting booking via API
        data = {
            "parent_id": self.parent.id,
            "lsa_id": self.lsa.id,
            "session_start": start.isoformat(),
            "session_end": end.isoformat()
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'BOOKING_CONFLICT')
