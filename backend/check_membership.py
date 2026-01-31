"""
Check club membership for ishansurdi
"""
import sys
import os
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from authentication.models import ClubMember

print("Checking membership for ishansurdi in GDSC (club_id=1)")
print("=" * 60)

member = ClubMember.objects.filter(user__username='ishansurdi', club_id=1).first()

if member:
    print(f"✅ Membership found!")
    print(f"User: {member.user.username}")
    print(f"Club: {member.club.name}")
    print(f"Role: {member.role}")
    print(f"Status: {member.status}")
    print(f"Joined: {member.joined_at}")
else:
    print("❌ No membership found")

print("\n" + "=" * 60)
print("All memberships for ishansurdi:")
print("=" * 60)

all_memberships = ClubMember.objects.filter(user__username='ishansurdi')
for m in all_memberships:
    print(f"Club: {m.club.name} | Role: {m.role} | Status: {m.status}")
