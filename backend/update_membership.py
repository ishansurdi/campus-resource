"""
Update membership status to active for testing
"""
import sys
import os
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from authentication.models import ClubMember

# Update all pending memberships to active
print("=" * 60)
print("Updating all pending memberships to active...")
print("=" * 60)

pending_members = ClubMember.objects.filter(status='pending')
count = pending_members.count()

if count == 0:
    print("✅ No pending memberships found. All memberships are active!")
else:
    print(f"Found {count} pending memberships:")
    for member in pending_members:
        print(f"  - {member.user.username} in {member.club.name} ({member.role})")
    
    # Update all to active
    pending_members.update(status='active')
    print(f"\n✅ Updated {count} memberships to 'active' status")
    print("All users can now submit event applications!")

print("=" * 60)
