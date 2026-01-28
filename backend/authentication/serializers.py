from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    AdminUser, UniversityProfile, ClubMember, RoleHistory, Club, 
    ApprovalRequest, ApprovalHistory, Event, EventCollaborator, EventLog, EventReport
)


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for AdminUser model."""
    
    class Meta:
        model = AdminUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'student_id', 'employee_id', 'department',
            'is_active', 'two_factor_enabled', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom user data to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'department': self.user.department,
        }
        
        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to JWT
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        
        return token


class LoginSerializer(serializers.Serializer):
    """Serializer for login request."""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    role = serializers.ChoiceField(
        choices=['student', 'faculty', 'admin', 'registrar'],
        required=False,
        allow_null=True
    )
    two_factor_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = AdminUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'student_id', 
            'employee_id', 'department'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = AdminUser.objects.create_user(**validated_data)
        return user


class UniversityProfileSerializer(serializers.ModelSerializer):
    """Serializer for university-wide settings."""

    class Meta:
        model = UniversityProfile
        fields = [
            'id', 'name', 'tagline', 'description',
            'logo_url', 'favicon_url', 'hero_image_url',
            'primary_color', 'secondary_color',
            'address', 'city', 'state', 'country', 'postal_code',
            'contact_email', 'contact_phone', 'website',
            'accreditation', 'founded_year',
            'storage_bucket', 'storage_region', 'storage_folder',
            'updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'updated_at', 'created_at']


class ClubMemberSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('treasurer', 'Treasurer'),
        ('secretary', 'Secretary'),
        ('faculty', 'Faculty Mentor'),
    ])
    department = serializers.CharField(max_length=128, required=False, allow_blank=True)
    academic_year = serializers.CharField(max_length=32, required=False, allow_blank=True)


class ClubMemberDetailSerializer(serializers.ModelSerializer):
    """Serializer for ClubMember model with full details."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, allow_null=True)
    revoked_by_name = serializers.CharField(source='revoked_by.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = ClubMember
        fields = [
            'id', 'club', 'user', 'user_name', 'user_email', 'role', 'status',
            'department', 'academic_year', 'created_at', 'approved_at', 
            'approved_by', 'approved_by_name', 'revoked_at', 'revoked_by', 'revoked_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'approved_at', 'approved_by', 'revoked_at', 'revoked_by']


class RoleHistorySerializer(serializers.ModelSerializer):
    """Serializer for RoleHistory model."""
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True, allow_null=True)
    club_member_info = serializers.SerializerMethodField()

    class Meta:
        model = RoleHistory
        fields = ['id', 'club_member', 'club_member_info', 'action', 'performed_by', 'performed_by_name', 'remarks', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def get_club_member_info(self, obj):
        return {
            'user_name': obj.club_member.user.get_full_name(),
            'role': obj.club_member.role,
            'club_name': obj.club_member.club.name
        }


class ClubSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    club_number = serializers.CharField(max_length=16)
    members = ClubMemberSerializer(many=True)


class ApprovalHistorySerializer(serializers.ModelSerializer):
    """Serializer for ApprovalHistory model."""
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = ApprovalHistory
        fields = [
            'id', 'approval_request', 'action', 'performed_by', 'performed_by_name',
            'field_changed', 'old_value', 'new_value', 'comment', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class ApprovalRequestSerializer(serializers.ModelSerializer):
    """Serializer for ApprovalRequest model with full details."""
    club_name = serializers.CharField(source='club.name', read_only=True)
    club_number = serializers.CharField(source='club.club_number', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True, allow_null=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, allow_null=True)
    rejected_by_name = serializers.CharField(source='rejected_by.get_full_name', read_only=True, allow_null=True)
    history = ApprovalHistorySerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'request_type', 'title', 'description', 'club', 'club_name', 'club_number',
            'amount', 'budget_category', 'event_date', 'event_location', 'expected_participants',
            'resource_name', 'quantity', 'resource_category', 'status', 'current_reviewer_role',
            'priority', 'requested_by', 'requested_by_name', 'approved_by', 'approved_by_name',
            'rejected_by', 'rejected_by_name', 'attachment_url', 'supporting_documents',
            'created_at', 'updated_at', 'reviewed_at', 'admin_notes', 'rejection_reason', 'history'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewed_at', 'approved_by', 'rejected_by']


class ApprovalRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating approval requests."""

    class Meta:
        model = ApprovalRequest
        fields = [
            'request_type', 'title', 'description', 'club', 'amount', 'budget_category',
            'event_date', 'event_location', 'expected_participants', 'resource_name',
            'quantity', 'resource_category', 'current_reviewer_role', 'priority', 'attachment_url'
        ]

    def validate(self, attrs):
        """Validate type-specific required fields."""
        request_type = attrs.get('request_type')
        
        if request_type == 'budget' and not attrs.get('amount'):
            raise serializers.ValidationError({"amount": "Amount is required for budget requests."})
        
        if request_type == 'event' and not attrs.get('event_date'):
            raise serializers.ValidationError({"event_date": "Event date is required for event requests."})
        
        if request_type == 'resource' and not attrs.get('resource_name'):
            raise serializers.ValidationError({"resource_name": "Resource name is required for resource requests."})
        
        return attrs

class EventCollaboratorSerializer(serializers.ModelSerializer):
    """Serializer for event collaborators."""
    club_name = serializers.CharField(source='club.name', read_only=True)
    coordinator_name = serializers.CharField(source='coordinator.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = EventCollaborator
        fields = [
            'id', 'event', 'club', 'club_name', 'role', 'status',
            'budget_contribution', 'resource_contribution', 'volunteer_count',
            'coordinator', 'coordinator_name', 'invited_at', 'responded_at', 'notes'
        ]
        read_only_fields = ['id', 'invited_at']


class EventLogSerializer(serializers.ModelSerializer):
    """Serializer for event logs."""
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = EventLog
        fields = [
            'id', 'event', 'action', 'performed_by', 'performed_by_name',
            'field_changed', 'old_value', 'new_value', 'description',
            'metadata', 'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class EventReportSerializer(serializers.ModelSerializer):
    """Serializer for event reports."""
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True, allow_null=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = EventReport
        fields = [
            'id', 'event', 'event_title', 'report_type', 'title', 'summary',
            'total_participants', 'total_expenses', 'total_revenue', 'budget_variance',
            'objectives_met', 'challenges_faced', 'lessons_learned', 'recommendations',
            'average_rating', 'feedback_count', 'feedback_summary',
            'photos_count', 'videos_count', 'media_urls', 'report_file_url',
            'supporting_documents', 'generated_by', 'generated_by_name',
            'generated_at', 'updated_at', 'is_published', 'published_at'
        ]
        read_only_fields = ['id', 'generated_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Event model."""
    primary_club_name = serializers.CharField(source='primary_club.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, allow_null=True)
    primary_coordinator_name = serializers.CharField(source='primary_coordinator.get_full_name', read_only=True, allow_null=True)
    collaborators = EventCollaboratorSerializer(many=True, read_only=True, source='collaborations')
    collaborator_count = serializers.SerializerMethodField()
    logs = EventLogSerializer(many=True, read_only=True)
    reports = EventReportSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'event_id', 'title', 'description', 'event_type', 'primary_club', 'primary_club_name',
            'collaborating_clubs', 'is_joint_event', 'start_date', 'end_date',
            'registration_start', 'registration_end', 'venue', 'venue_address',
            'is_online', 'online_meeting_link', 'max_participants', 'current_registrations',
            'requires_registration', 'registration_fee', 'estimated_budget', 'approved_budget',
            'actual_expense', 'budget_category', 'sponsorship_amount', 'status', 'visibility',
            'requires_approval', 'approval_request', 'created_by', 'created_by_name',
            'approved_by', 'approved_by_name', 'cancelled_by', 'primary_coordinator',
            'primary_coordinator_name', 'contact_email', 'contact_phone', 'poster_url',
            'banner_url', 'gallery_urls', 'attachments', 'actual_participants',
            'feedback_collected', 'report_generated', 'report_url', 'success_rating',
            'featured', 'priority', 'tags', 'notes', 'rejection_reason', 'cancellation_reason',
            'created_at', 'updated_at', 'approved_at', 'cancelled_at', 'closed_at',
            'collaborators', 'collaborator_count', 'logs', 'reports'
        ]
        read_only_fields = [
            'id', 'event_id', 'created_at', 'updated_at', 'approved_at', 
            'cancelled_at', 'closed_at', 'approved_by', 'cancelled_by'
        ]

    def get_collaborator_count(self, obj):
        return obj.collaborations.count()


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events."""

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'primary_club', 'is_joint_event',
            'start_date', 'end_date', 'registration_start', 'registration_end',
            'venue', 'venue_address', 'is_online', 'online_meeting_link',
            'max_participants', 'requires_registration', 'registration_fee',
            'estimated_budget', 'budget_category', 'primary_coordinator',
            'contact_email', 'contact_phone', 'visibility', 'tags'
        ]

    def validate(self, attrs):
        """Validate event dates."""
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})
        
        if attrs.get('registration_start') and attrs.get('registration_end'):
            if attrs['registration_start'] >= attrs['registration_end']:
                raise serializers.ValidationError({"registration_end": "Registration end must be after start."})
        
        return attrs