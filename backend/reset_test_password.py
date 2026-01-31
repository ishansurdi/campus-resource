"""
Reset password for a user
"""
import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from authentication.models import AdminUser

username = "ishansurdi"
new_password = "test123"

try:
    user = AdminUser.objects.get(username=username)
    user.set_password(new_password)
    user.save()
    print(f"✅ Password reset successful for {username}")
    print(f"New password: {new_password}")
except AdminUser.DoesNotExist:
    print(f"❌ User {username} not found")
