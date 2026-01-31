from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import event_views
from . import application_views

urlpatterns = [
    # Authentication endpoints
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # JWT token endpoints
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', views.user_profile_view, name='user_profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('my-clubs/', views.my_clubs_view, name='my_clubs'),

    # University profile
    path('university/', views.university_profile_view, name='university_profile'),
    path('university/upload/', views.university_upload_view, name='university_upload'),
    path('clubs/', views.clubs_view, name='clubs'),
    path('clubs/all/', views.all_clubs_view, name='all_clubs'),
    path('clubs/<int:club_id>/', views.club_detail_view, name='club_detail'),
    path('clubs/<int:club_id>/members/', views.club_members_view, name='club_members'),
    
    # Club Applications
    path('club-applications/', views.club_applications_view, name='club_applications'),
    path('club-applications/<int:application_id>/', views.application_detail_view, name='application_detail'),
    
    # Role Management endpoints
    path('membership-requests/', views.membership_requests_view, name='membership_requests'),
    path('approve-role/<int:member_id>/', views.approve_role_view, name='approve_role'),
    path('revoke-access/<int:member_id>/', views.revoke_access_view, name='revoke_access'),
    path('role-history/', views.role_history_view, name='role_history'),
    
    # Approval Management endpoints
    path('approvals/', views.approvals_view, name='approvals'),
    path('approvals/<int:approval_id>/', views.approval_detail_view, name='approval_detail'),
    path('approvals/<int:approval_id>/approve/', views.approve_request_view, name='approve_request'),
    path('approvals/<int:approval_id>/reject/', views.reject_request_view, name='reject_request'),
    path('approvals/<int:approval_id>/review/', views.mark_under_review_view, name='mark_under_review'),
    path('approvals/<int:approval_id>/history/', views.approval_history_view, name='approval_history'),
    
    # Event Management endpoints
    path('events/', event_views.events_list_view, name='events_list'),
    path('events/<int:event_id>/', event_views.event_detail_view, name='event_detail'),
    path('event-registrations/', event_views.event_registrations_view, name='event_registrations'),
    path('my-event-attendances/', event_views.my_event_attendances_view, name='my_event_attendances'),
    path('my-certificates/', event_views.my_certificates_view, name='my_certificates'),
    path('event-feedback/<int:attendance_id>/', event_views.submit_event_feedback_view, name='submit_event_feedback'),
    
    # Event Application & Approval endpoints
    path('event-application/submit/', event_views.submit_event_application_view, name='submit_event_application'),
    path('my-event-applications/', event_views.my_event_applications_view, name='my_event_applications'),
    path('event-applications/pending-faculty/', event_views.pending_faculty_approvals_view, name='pending_faculty_approvals'),
    path('event-applications/pending-admin/', event_views.pending_admin_approvals_view, name='pending_admin_approvals'),
    path('event-applications/<int:event_id>/faculty-approve/', event_views.faculty_approve_event_view, name='faculty_approve_event'),
    path('event-applications/<int:event_id>/faculty-reject/', event_views.faculty_reject_event_view, name='faculty_reject_event'),
    path('event-applications/<int:event_id>/admin-approve/', event_views.admin_approve_event_view, name='admin_approve_event'),
    path('event-applications/<int:event_id>/admin-reject/', event_views.admin_reject_event_view, name='admin_reject_event'),
    
    # Club Application & Approval endpoints
    path('club-application/submit/', application_views.submit_club_application_view, name='submit_club_application'),
    path('my-club-applications/', application_views.my_club_applications_view, name='my_club_applications'),
    path('club-applications/pending-faculty/', application_views.pending_faculty_club_applications_view, name='pending_faculty_club_applications'),
    path('club-applications/pending-admin/', application_views.pending_admin_club_applications_view, name='pending_admin_club_applications'),
    path('club-applications/<int:application_id>/faculty-approve/', application_views.faculty_approve_club_application_view, name='faculty_approve_club_application'),
    path('club-applications/<int:application_id>/faculty-reject/', application_views.faculty_reject_club_application_view, name='faculty_reject_club_application'),
    path('club-applications/<int:application_id>/admin-approve/', application_views.admin_approve_club_application_view, name='admin_approve_club_application'),
    path('club-applications/<int:application_id>/admin-reject/', application_views.admin_reject_club_application_view, name='admin_reject_club_application'),
    path('club-applications/<int:application_id>/implement/', application_views.implement_club_application_view, name='implement_club_application'),
    
    # Event Expense Management (for organizers)
    path('events/<int:event_id>/expenses/', event_views.event_expenses_view, name='event_expenses'),
    path('events/<int:event_id>/expenses/add/', event_views.add_event_expense_view, name='add_event_expense'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
