from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    
    def ready(self):
        """
        Called when Django starts - ensure admin user exists
        """
        # Only run once, not in reloader
        import os
        import sys
        
        # Skip if running migrations or other management commands
        if 'manage.py' in sys.argv[0] and len(sys.argv) > 1:
            if sys.argv[1] in ['migrate', 'makemigrations', 'collectstatic']:
                return
        
        # Skip in reloader process
        if os.environ.get('RUN_MAIN') == 'true':
            return
            
        try:
            # Import here to avoid AppRegistryNotReady error
            from django.db import connection
            from authentication.models import AdminUser
            
            # Check if database is ready
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            username = 'admin'
            password = 'Admin@123'
            email = 'admin@campusphere.edu'
            
            # Check if admin exists
            if not AdminUser.objects.filter(username=username).exists():
                # Create admin user
                AdminUser.objects.create_user(
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
                print(f'✓ Admin user "{username}" created on startup')
                
        except Exception as e:
            # Silently skip if database not ready
            pass
