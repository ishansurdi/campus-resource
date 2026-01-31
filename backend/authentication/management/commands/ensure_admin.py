"""
Django management command to ensure admin user exists
This will be run automatically during deployment
"""
from django.core.management.base import BaseCommand
from authentication.models import AdminUser


class Command(BaseCommand):
    help = 'Create default admin user if it does not exist'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = 'Admin@123'
        email = 'admin@campusphere.edu'
        
        try:
            # Check if admin already exists
            if AdminUser.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Admin user "{username}" already exists')
                )
                return
            
            # Create admin user
            admin = AdminUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='System',
                last_name='Administrator',
                role='admin',
                employee_id='EMP001',
                department='Information Technology',
                is_staff=True,
                is_superuser=True,
                is_active=True,
                two_factor_enabled=False
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Admin user created successfully!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'  Username: {username}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'  Password: {password}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'  Email: {email}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating admin user: {str(e)}')
            )
            raise
