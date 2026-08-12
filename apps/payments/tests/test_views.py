from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from apps.parents.models import Parent
from apps.lsas.models import LSAProfile
from apps.bookings.models import BookingRequest, BookingStatus
from apps.payments.models import Payment, PaymentStatus
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
import json

class WebhookViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('razorpay-webhook')
        
        self.parent = Parent.objects.create(name="Test Parent", email="parent@example.com")
        self.lsa = LSAProfile.objects.create(
            name="Test LSA", 
            email="lsa@example.com",
            hourly_rate=Decimal("1000.00"),
            is_active=True
        )
        now = timezone.now()
        start = now + timedelta(days=1, hours=10)
        end = start + timedelta(hours=1)
        
        self.booking = BookingRequest.objects.create(
            parent=self.parent,
            lsa=self.lsa,
            session_start=start,
            session_end=end,
            status=BookingStatus.PENDING
        )
        
        self.payment = Payment.objects.create(
            booking=self.booking,
            razorpay_order_id="order_123",
            amount=100000,
            currency='INR',
            status=PaymentStatus.CREATED
        )

    @patch('apps.payments.views.RazorpayClient')
    def test_webhook_payment_captured(self, mock_client_class):
        mock_instance = mock_client_class.return_value
        mock_instance.verify_webhook_signature.return_value = True
        
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_456",
                        "order_id": "order_123"
                    }
                }
            }
        }
        
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json', HTTP_X_RAZORPAY_SIGNATURE='fake_sig')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.payment.refresh_from_db()
        self.booking.refresh_from_db()
        
        self.assertEqual(self.payment.status, PaymentStatus.SUCCESS)
        self.assertEqual(self.payment.razorpay_payment_id, "pay_456")
        self.assertEqual(self.booking.status, BookingStatus.CONFIRMED)

    @patch('apps.payments.views.RazorpayClient')
    def test_webhook_invalid_signature(self, mock_client_class):
        mock_instance = mock_client_class.return_value
        mock_instance.verify_webhook_signature.return_value = False
        
        payload = {"event": "payment.captured"}
        
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json', HTTP_X_RAZORPAY_SIGNATURE='fake_sig')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_webhook_missing_signature(self):
        payload = {"event": "payment.captured"}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
