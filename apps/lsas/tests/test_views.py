from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from apps.parents.models import Parent
from apps.lsas.models import LSAProfile
from apps.bookings.services import create_booking
from decimal import Decimal
from django.contrib.auth.models import User
from unittest.mock import patch
import apps.payments.services

class LSASearchViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('lsa-search')

        self.lsa1 = LSAProfile.objects.create(
            name="Autism Specialist 1", 
            email="lsa1@example.com",
            skills=['autism', 'adhd'],
            hourly_rate=Decimal("1500.00"),
            is_active=True
        )
        self.lsa2 = LSAProfile.objects.create(
            name="Math Tutor", 
            email="lsa2@example.com",
            skills=['math'],
            hourly_rate=Decimal("800.00"),
            is_active=True
        )
        self.lsa3 = LSAProfile.objects.create(
            name="Autism Specialist 2", 
            email="lsa3@example.com",
            skills=['autism'],
            hourly_rate=Decimal("1200.00"),
            is_active=True
        )
        self.parent = Parent.objects.create(name="Test Parent", email="parent@example.com")

        # Mock Razorpay
        self.patcher = patch('apps.payments.services.RazorpayClient')
        self.mock_client = self.patcher.start()
        self.mock_client.return_value.create_order.return_value = {'id': 'order_mock123'}

    def tearDown(self):
        self.patcher.stop()

        
    def test_search_by_skill(self):

        response = self.client.get(self.url, {'skill': 'autism'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['results']), 2)
        
    def test_search_availability(self):
        now = timezone.now()
        start = now + timedelta(days=2)
        end = start + timedelta(hours=2)

        
        # Book lsa1 for this time
        create_booking(self.parent, self.lsa1, start, end)
        
        response = self.client.get(self.url, {
            'skill': 'autism',
            'session_start': start.isoformat(),
            'session_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['id'], self.lsa3.id)

    def test_n_plus_one_query(self):

        # Create many LSAs to ensure no N+1 query issue
        for i in range(20):
            LSAProfile.objects.create(
                name=f"Bulk LSA {i}",
                email=f"bulk{i}@example.com",
                skills=['autism'],
                hourly_rate=Decimal("1000.00"),
                is_active=True
            )
        
        now = timezone.now()
        start = now + timedelta(days=3)
        end = start + timedelta(hours=1)
        
        with self.assertNumQueries(2):
            # 1 query for COUNT (pagination)
            # 1 query for fetching LSAs
            response = self.client.get(self.url, {
                'skill': 'autism',
                'session_start': start.isoformat(),
                'session_end': end.isoformat()
            }, format='json')
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # 2 original + 20 bulk = 22 total with 'autism' skill
        # Paginated at 10 per page
        self.assertEqual(len(response.data['data']['results']), 10)
        self.assertEqual(response.data['data']['count'], 22)
