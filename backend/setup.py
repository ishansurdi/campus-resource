"""
Setup script for CAMPUSPHERE backend.
Creates database, runs migrations, and creates a test admin user.
"""
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from django.core.management import call_command
from authentication.models import AdminUser


def setup_database():
    """Run migrations and create database tables."""
    print("🔄 Running database migrations...")
    try:
        call_command('makemigrations', 'authentication')
        call_command('migrate')
        print("✅ Database migrations completed successfully!")
    except Exception as e:
        print(f"❌ Error during migrations: {e}")
        return False
    return True


def create_test_admin():
    """Create a test admin user."""
    print("\n🔄 Creating test admin user...")
    
    try:
        # Check if admin already exists
        if AdminUser.objects.filter(username='admin').exists():
            print("ℹ️  Admin user already exists. Skipping creation.")
            return True
        
        # Create admin user
        admin = AdminUser.objects.create_user(
            username='admin',
            email='admin@campusphere.edu',
            password='Admin@123',
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
        
        print("✅ Test admin user created successfully!")
        print("\n📋 Login Credentials:")
        print(f"   Username: admin")
        print(f"   Password: Admin@123")
        print(f"   Email: admin@campusphere.edu")
        print(f"   Role: Administrator")
        
        return True
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("🚀 CAMPUSPHERE Backend Setup")
    print("=" * 60)
    
    # Setup database
    if not setup_database():
        print("\n❌ Setup failed during database migration.")
        return
    
    # Create test users
    if not create_test_admin():
        print("\n❌ Setup failed during admin user creation.")
        return
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print("\n📚 Next Steps:")
    print("   1. Start the development server:")
    print("      python manage.py runserver")
    print("\n   2. Test the API:")
    print("      Health Check: http://localhost:8000/api/auth/health/")
    print("      Login: POST http://localhost:8000/api/auth/login/")
    print("=" * 60)


if __name__ == '__main__':
    main()
