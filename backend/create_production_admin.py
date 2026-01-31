"""
Create admin user in production database
Run this on Render or any production environment to create the initial admin user
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from authentication.models import AdminUser


def create_admin_user():
    """Create admin user if it doesn't exist."""
    username = 'admin'
    password = 'Admin@123'
    
    try:
        # Check if admin already exists
        if AdminUser.objects.filter(username=username).exists():
            admin = AdminUser.objects.get(username=username)
            print(f"✅ Admin user '{username}' already exists!")
            print(f"\n📋 Login Credentials:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"   Email: {admin.email}")
            print(f"   Role: {admin.role}")
            return True
        
        # Create new admin user
        admin = AdminUser.objects.create_user(
            username=username,
            email='admin@campusphere.edu',
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
        
        print("✅ Admin user created successfully!")
        print("\n📋 Login Credentials:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: admin@campusphere.edu")
        print(f"   Role: Administrator")
        print(f"\n🌐 Access the application at:")
        print(f"   Frontend: https://campusphere-frontend-5sm4.onrender.com/login.html")
        print(f"   Backend: https://campus-resource-8pw5.onrender.com/admin/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 70)
    print("Creating Admin User for CAMPUSPHERE Production Database")
    print("=" * 70)
    print()
    
    success = create_admin_user()
    
    print()
    print("=" * 70)
    
    if success:
        print("✅ Setup completed successfully!")
    else:
        print("❌ Setup failed. Please check the error messages above.")
    
    print("=" * 70)
