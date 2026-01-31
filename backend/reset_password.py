"""
Reset password for ishansurdi2105 to match the admin email credentials.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from authentication.models import AdminUser

# Find and update user
try:
    user = AdminUser.objects.get(username='ishansurdi2105')
    
    print(f"\n✅ Found user: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role}")
    print(f"   Active: {user.is_active}")
    
    # Reset password
    user.set_password('1cLpNrUD3Um-rA')
    user.save()
    
    print(f"\n✅ Password reset successfully!")
    print(f"\n📋 Login Credentials:")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Password: 1cLpNrUD3Um-rA")
    print(f"\n   You can now login with either username or email.")
    
except AdminUser.DoesNotExist:
    print(f"\n❌ User 'ishansurdi2105' not found")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
