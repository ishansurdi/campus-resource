"""
Quick script to check if user exists and create test student.
Run this from backend directory: python check_user.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusphere.settings')
django.setup()

from authentication.models import AdminUser

def check_user(username_or_email):
    """Check if a user exists by username or email"""
    print(f"\n{'='*60}")
    print(f"Checking user: {username_or_email}")
    print(f"{'='*60}\n")
    
    user = None
    
    # Try by username
    try:
        user = AdminUser.objects.get(username=username_or_email)
        print(f"✅ Found user by USERNAME")
    except AdminUser.DoesNotExist:
        print(f"❌ Not found by username")
    
    # Try by email if not found
    if not user:
        try:
            user = AdminUser.objects.get(email=username_or_email)
            print(f"✅ Found user by EMAIL")
        except AdminUser.DoesNotExist:
            print(f"❌ Not found by email")
    
    if user:
        print(f"\n📋 User Details:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   First Name: {user.first_name}")
        print(f"   Last Name: {user.last_name}")
        print(f"   Role: {user.role}")
        print(f"   Student ID: {user.student_id}")
        print(f"   Department: {user.department}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Date Joined: {user.date_joined}")
        return user
    else:
        print(f"\n❌ User '{username_or_email}' does not exist in database")
        return None

def create_test_student():
    """Create a test student account"""
    print(f"\n{'='*60}")
    print(f"Creating Test Student Account")
    print(f"{'='*60}\n")
    
    # Check if already exists
    if AdminUser.objects.filter(username='ishansurdi2105').exists():
        print("⚠️  User 'ishansurdi2105' already exists!")
        user = AdminUser.objects.get(username='ishansurdi2105')
        
        # Update password
        user.set_password('1cLpNrUD3Um-rA')
        user.save()
        print("✅ Password updated to: 1cLpNrUD3Um-rA")
        return user
    
    # Create new user
    try:
        user = AdminUser.objects.create_user(
            username='ishansurdi2105',
            email='ishansurdi2105@campus.edu',
            password='1cLpNrUD3Um-rA',
            first_name='Ishan',
            last_name='Surdi',
            role='student',
            student_id='ishansurdi2105',
            department='Computer Science'
        )
        
        print("✅ Test student created successfully!")
        print(f"\n📋 Login Credentials:")
        print(f"   Username: ishansurdi2105")
        print(f"   Email: ishansurdi2105@campus.edu")
        print(f"   Password: 1cLpNrUD3Um-rA")
        print(f"   Role: student")
        
        return user
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        return None

def list_all_students():
    """List all student accounts"""
    print(f"\n{'='*60}")
    print(f"All Student Accounts")
    print(f"{'='*60}\n")
    
    students = AdminUser.objects.filter(role='student')
    
    if students.exists():
        for idx, student in enumerate(students, 1):
            print(f"{idx}. {student.username} ({student.email}) - {student.get_full_name()}")
            print(f"   Active: {student.is_active}, Joined: {student.date_joined.strftime('%Y-%m-%d')}")
        print(f"\n📊 Total students: {students.count()}")
    else:
        print("❌ No student accounts found")

if __name__ == '__main__':
    print("\n🎓 CAMPUSPHERE - User Management Tool\n")
    
    # List all students
    list_all_students()
    
    # Check for specific user
    print("\n" + "="*60)
    username = input("\nEnter username or email to check (or press Enter to create test student): ").strip()
    
    if username:
        check_user(username)
    else:
        create_test_student()
    
    print("\n✅ Done!\n")
