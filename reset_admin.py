import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bachata_club.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import Membership
from django.utils import timezone
import datetime

# Delete existing admin if it exists
User.objects.filter(username='admin').delete()

# Create new admin user with correct password
admin = User.objects.create_superuser(
    username='admin',
    email='admin@bachataclub.com',
    password='Admin123!'
)

print(f"✓ Created admin user: {admin.username}")

# Create active membership for admin
membership, created = Membership.objects.get_or_create(user=admin)
membership.status = Membership.STATUS_ACTIVE
membership.current_period_end = timezone.now() + datetime.timedelta(days=365)
membership.save()

print(f"✓ Created membership for admin")
print(f"  Status: {membership.status}")
print(f"  Access: {membership.has_access}")
print(f"  Period ends: {membership.current_period_end}")

# Verify authentication works
from django.contrib.auth import authenticate
test_auth = authenticate(username='admin', password='Admin123!')
if test_auth:
    print(f"\n✓ Authentication verified: {test_auth.username}")
else:
    print(f"\n✗ Authentication FAILED")

print(f"\nAdmin can now log in at:")
print(f"  - /admin/ (Django admin)")
print(f"  - /accounts/login/ (Member login)")
