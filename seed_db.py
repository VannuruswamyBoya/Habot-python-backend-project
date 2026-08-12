import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.parents.models import Parent
from apps.lsas.models import LSAProfile
from decimal import Decimal

def seed():
    # 1. Create a test API User (for JWT login)
    if not User.objects.filter(username='anil').exists():
        User.objects.create_user(username='anil', password='anil07')
        print("Created test user: anil / anil07")
    else:
        print("Test user already exists.")

    # 2. Create a test Parent (to make bookings for)
    parent, created = Parent.objects.get_or_create(
        email='chandra3@gmail.com',
        defaults={'name': 'githa', 'phone': '2234567899'}
    )
    if created:
        print(f"Created Parent: githa (ID: {parent.id})")
    else:
        print(f"Parent githa already exists (ID: {parent.id})")

    # 3. Create some test LSAs
    lsa1, created = LSAProfile.objects.get_or_create(
        email='lsa1@gmail.com',
        defaults={
            'name': 'LSA 1', 
            'skills': ['autism', 'math'], 
            'hourly_rate': Decimal('1500.00'),
            'is_active': True
        }
    )
    if created:
        print(f"Created LSA: LSA 1 (ID: {lsa1.id})")
        
    lsa2, created = LSAProfile.objects.get_or_create(
        email='lsa2@gmail.com',
        defaults={
            'name': 'LSA 2', 
            'skills': ['adhd', 'reading'], 
            'hourly_rate': Decimal('1200.00'),
            'is_active': True
        }
    )
    if created:
        print(f"Created LSA: LSA 2 (ID: {lsa2.id})")

if __name__ == '__main__':
    seed()
