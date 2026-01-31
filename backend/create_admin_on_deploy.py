#!/usr/bin/env python
"""
Alternate build script to create admin user
Can be called directly with: python create_admin_on_deploy.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from authentication.models import AdminUser

def create_admin():
    username = 'admin'
    password = 'Admin@123'
    email = 'admin@campusphere.edu'
    
    try:
        # Check if admin exists
        if AdminUser.objects.filter(username=username).exists():
            print(f'✓ Admin user "{username}" already exists')
            admin = AdminUser.objects.get(username=username)
            print(f'  Email: {admin.email}')
            print(f'  Role: {admin.role}')
            print(f'  Active: {admin.is_active}')
            return True
        
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
        
        print('✓ Admin user created successfully!')
        print(f'  Username: {username}')
        print(f'  Password: {password}')
        print(f'  Email: {email}')
        return True
        
    except Exception as e:
        print(f'✗ Error: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('Creating Admin User')
    print('=' * 60)
    success = create_admin()
    print('=' * 60)
    sys.exit(0 if success else 1)
