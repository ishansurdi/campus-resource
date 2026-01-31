"""
Test script for event application submission
Tests the submit_event_application_view endpoint with sample data
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api/auth/event-application/submit/"

# Test credentials - using student login
USERNAME = "ishansurdi"  # Student username (treasurer of GDSC)
PASSWORD = "test123"  # Test password

def get_jwt_token():
    """Get JWT access token"""
    login_url = f"{BASE_URL}/api/auth/login/"
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    print(f"🔑 Logging in as {USERNAME}...")
    response = requests.post(login_url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access')
        print(f"✅ Login successful! Got access token")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def submit_event_application(token):
    """Submit event application with test data"""
    
    # Test data matching the user's form
    test_data = {
        "club_id": 1,  # Assuming GDSC is club ID 1
        "title": "Test Hackathon Event",  # Changed from event_name to title
        "event_type": "technical",
        "description": "A comprehensive hackathon event to test the submission system. Students will work on innovative projects.",
        "start_date": "2026-02-01",
        "end_date": "2026-03-01",
        "venue": "Central Hall",
        "expected_participants": 500,
        "registration_fee": 83.00,
        "estimated_budget": 30000.00,  # Changed from budget to estimated_budget
        "faculty_mentor_name": "Dr. Rao",
        "faculty_mentor_email": "ishansurdi@gmail.com",
        "faculty_mentor_department": "CSE",
        "target_audience": "All engineering students interested in coding and innovation",
        "objectives": "To foster innovation, collaboration, and technical skills development",
        "resources_needed": "Computers, projectors, WiFi access, refreshments",
        "agenda": "Day 1: Registration and problem statements\nDay 2-28: Development phase\nDay 29: Final presentations",
        "sponsors": "Tech companies and local businesses"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📤 Submitting event application...")
    print(f"URL: {API_URL}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(API_URL, json=test_data, headers=headers)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print(f"✅ SUCCESS! Event application submitted")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ FAILED with status {response.status_code}")
            print(f"Response: {response.text}")
            
            # Check if it's CSRF error
            if response.status_code == 403:
                print(f"\n⚠️ 403 Forbidden - Possible CSRF or Permission issue")
                print(f"This could be due to:")
                print(f"  1. Server not restarted after adding @csrf_exempt")
                print(f"  2. @csrf_exempt not working with @api_view decorator")
                print(f"  3. Permission issue with club membership")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error - Is the Django server running?")
        print(f"Start server with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("=" * 60)
    print("🧪 Testing Event Application Submission")
    print("=" * 60)
    
    # Step 1: Get JWT token
    token = get_jwt_token()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Step 2: Submit event application
    print(f"\n" + "=" * 60)
    success = submit_event_application(token)
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - Event application submitted successfully!")
    else:
        print("❌ TEST FAILED - Event application submission failed")
    print("=" * 60)

if __name__ == "__main__":
    main()
