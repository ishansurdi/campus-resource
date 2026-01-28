from django.core.management.base import BaseCommand
from authentication.models import AdminUser, Club


class Command(BaseCommand):
    help = 'Update faculty mentor names from club member data'

    def handle(self, *args, **options):
        # Get all clubs
        clubs = Club.objects.filter(faculty_mentor__isnull=False)
        
        updated_count = 0
        for club in clubs:
            faculty_user = club.faculty_mentor
            
            # Try to get the faculty member data from club members
            faculty_members = club.members.filter(role='faculty')
            
            if faculty_members.exists():
                faculty_member = faculty_members.first()
                # Extract name from the stored member data if available
                # Since we don't have a name field in ClubMember, we'll use the user's email to infer
                pass
            
            # If faculty user has no name, try to extract from email or prompt
            if not faculty_user.first_name and not faculty_user.last_name:
                # Extract name from email (e.g., dr.rao@... -> Dr Rao)
                email_name = faculty_user.email.split('@')[0].replace('.', ' ').title()
                
                # Ask for confirmation or use a reasonable guess
                if email_name != faculty_user.username:
                    parts = email_name.split(maxsplit=1)
                    faculty_user.first_name = parts[0] if len(parts) > 0 else ''
                    faculty_user.last_name = parts[1] if len(parts) > 1 else ''
                    faculty_user.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated {faculty_user.email}: {faculty_user.get_full_name()}"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} faculty members')
        )
