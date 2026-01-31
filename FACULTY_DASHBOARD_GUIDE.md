# Faculty Dashboard Login Guide

## Access the Faculty Dashboard

**URL:** `file:///C:/Users/Admin/Desktop/Restart/Projects/campusresource/frontend/dashboards/faculty-dashboard/faculty-dashboard.html`

Or navigate to:
```
frontend/dashboards/faculty-dashboard/faculty-dashboard.html
```

## Faculty Login Credentials

Based on your database, here are the faculty users:

**Username:** `pallavisurdi`  
**Password:** (your password)  
**Role:** Faculty  
**Clubs:** GDSC, Finance-cops, MDSC, Arts, Kala

## What You'll See

### Dashboard Overview
1. **Stats Cards** - Total pending items, applications, and events
2. **My Clubs** - All clubs where you're assigned as faculty mentor
3. **Pending Club Applications** - Applications awaiting your approval
4. **Pending Event Approvals** - Event requests from your clubs

### Features
- ✅ View all pending applications for your clubs
- ✅ Approve/Reject club applications with comments
- ✅ Approve/Reject event requests with reasons
- ✅ Clean CAMPUSPHERE design matching other dashboards
- ✅ Real-time updates after approval/rejection

## How to Test

1. **Login as faculty:**
   - Go to `frontend/login.html`
   - Username: `pallavisurdi`
   - Password: (your password)

2. **Navigate to Faculty Dashboard:**
   - After login, manually go to `faculty-dashboard.html`
   - OR add a link from the login page

3. **Test Approvals:**
   - You should see any applications/events with status `pending_faculty`
   - Click "Approve" to move them to `pending_admin`
   - Click "Reject" to reject them

## Next Steps

To make the dashboard fully functional, you may want to:
- [ ] Add navigation link from login page to faculty dashboard
- [ ] Create event approval endpoints (currently calling non-existent endpoints)
- [ ] Add email notifications on approval/rejection
- [ ] Add filtering by club
- [ ] Add search functionality

## Testing Password Reset

If you don't know the faculty password, run:
```bash
cd backend
python reset_test_password.py
```

Then update the script to use `pallavisurdi` instead of `ishansurdi`.
