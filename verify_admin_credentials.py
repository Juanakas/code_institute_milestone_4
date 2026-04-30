import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bachata_club.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

print("=" * 60)
print("COMPREHENSIVE ADMIN CREDENTIALS VERIFICATION")
print("=" * 60)

# 1. Check if admin user exists
try:
    admin = User.objects.get(username='admin')
    print("\n✓ Admin user EXISTS in database")
except User.DoesNotExist:
    print("\n✗ Admin user NOT FOUND in database")
    exit(1)

# 2. Check user properties
print("\n--- User Account Properties ---")
print(f"  Username: {admin.username}")
print(f"  Email: {admin.email}")
print(f"  Is Active: {admin.is_active}")
print(f"  Is Staff: {admin.is_staff}")
print(f"  Is Superuser: {admin.is_superuser}")
print(f"  Password Hash: {admin.password[:30]}...")

# Verify all admin permissions are set
if not admin.is_active:
    print("\n✗ ERROR: Admin account is NOT ACTIVE")
if not admin.is_staff:
    print("\n✗ ERROR: Admin account does NOT have staff status")
if not admin.is_superuser:
    print("\n✗ ERROR: Admin account is NOT a superuser")

# 3. Test authentication with provided password
print("\n--- Authentication Test ---")
auth_user = authenticate(username='admin', password='Admin123!')
if auth_user:
    print(f"✓ Authentication SUCCESSFUL with password 'Admin123!'")
    print(f"  Authenticated user: {auth_user.username}")
    print(f"  Same user object: {auth_user.id == admin.id}")
else:
    print(f"✗ Authentication FAILED with password 'Admin123!'")
    print(f"  The password may be incorrect")

# 4. Test with wrong password
print("\n--- Wrong Password Test ---")
wrong_auth = authenticate(username='admin', password='wrongpassword')
if wrong_auth is None:
    print(f"✓ Correctly REJECTED wrong password")
else:
    print(f"✗ Accepted wrong password (SECURITY ISSUE!)")

# 5. Check membership for member portal access
print("\n--- Membership Status ---")
try:
    membership = admin.membership
    print(f"✓ Admin has membership")
    print(f"  Status: {membership.status}")
    print(f"  Has access: {membership.has_access}")
    print(f"  Period end: {membership.current_period_end}")
except:
    print(f"✗ Admin does NOT have membership")

# 6. Summary
print("\n" + "=" * 60)
print("FINAL VERDICT:")
print("=" * 60)

all_good = (
    admin.is_active and
    admin.is_staff and
    admin.is_superuser and
    auth_user is not None
)

if all_good:
    print("✓✓✓ ADMIN CREDENTIALS ARE VALID ✓✓✓")
    print("\nThe admin user can:")
    print("  • Log in with username: admin")
    print("  • Log in with password: Admin123!")
    print("  • Access /admin/ (Django admin panel)")
    print("  • Access member portal as administrator")
else:
    print("✗✗✗ THERE ARE ISSUES WITH ADMIN CREDENTIALS ✗✗✗")
    print("\nPlease review the errors above")
