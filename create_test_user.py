import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bachata_club.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import Membership
from django.utils import timezone
import datetime

# Create test user if doesn't exist
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    
    # Create active membership
    membership, _ = Membership.objects.get_or_create(user=user)
    membership.status = Membership.STATUS_ACTIVE
    membership.current_period_end = timezone.now() + datetime.timedelta(days=30)
    membership.save()
    
    print(f"Created test user: {user.username}")
    print(f"Created membership: {membership}")
else:
    print(f"Test user already exists: {user.username}")
    membership = getattr(user, 'membership', None)
    print(f"Membership: {membership}")

print(f"User ID: {user.id}")
