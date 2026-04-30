import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bachata_club.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import Membership

admin = User.objects.get(username='admin')
print(f'Admin user: {admin}')
print(f'Is superuser: {admin.is_superuser}')
print(f'Is staff: {admin.is_staff}')
print(f'Is active: {admin.is_active}')

membership = getattr(admin, 'membership', None)
print(f'\nHas membership: {membership is not None}')

if membership:
    print(f'Membership status: {membership.status}')
    print(f'Has access: {membership.has_access}')
    print(f'Current period end: {membership.current_period_end}')
else:
    print("Admin user does NOT have a membership!")
