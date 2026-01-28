from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

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

    # University profile
    path('university/', views.university_profile_view, name='university_profile'),
    path('university/upload/', views.university_upload_view, name='university_upload'),
    path('clubs/', views.clubs_view, name='clubs'),
    
    # Role Management endpoints
    path('membership-requests/', views.membership_requests_view, name='membership_requests'),
    path('approve-role/<int:member_id>/', views.approve_role_view, name='approve_role'),
    path('revoke-access/<int:member_id>/', views.revoke_access_view, name='revoke_access'),
    path('role-history/', views.role_history_view, name='role_history'),
    path('clubs/<int:club_id>/members/', views.club_members_view, name='club_members'),
    
    # Approval Management endpoints
    path('approvals/', views.approvals_view, name='approvals'),
    path('approvals/<int:approval_id>/', views.approval_detail_view, name='approval_detail'),
    path('approvals/<int:approval_id>/approve/', views.approve_request_view, name='approve_request'),
    path('approvals/<int:approval_id>/reject/', views.reject_request_view, name='reject_request'),
    path('approvals/<int:approval_id>/review/', views.mark_under_review_view, name='mark_under_review'),
    path('approvals/<int:approval_id>/history/', views.approval_history_view, name='approval_history'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
