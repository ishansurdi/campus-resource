"""
Check existing users in the database
"""
import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from authentication.models import AdminUser, Club, ClubMember

print("=" * 60)
print("👥 Existing Users:")
print("=" * 60)

users = AdminUser.objects.all()[:10]
for user in users:
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Role: {user.role}")
    print(f"Active: {user.is_active}")
    print("-" * 40)

print("\n" + "=" * 60)
print("🏛️ Existing Clubs:")
print("=" * 60)

clubs = Club.objects.all()
for club in clubs:
    print(f"ID: {club.id} | Name: {club.name}")
    members = ClubMember.objects.filter(club=club)
    print(f"Members: {members.count()}")
    for member in members[:3]:
        print(f"  - {member.user.username} ({member.role})")
    print("-" * 40)
