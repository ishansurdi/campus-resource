from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings


class AdminUserManager(BaseUserManager):
    """Custom manager for AdminUser model."""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)


class AdminUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for CAMPUSPHERE system.
    Supports multiple roles: admin, student, faculty, registrar
    """
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('registrar', 'Registrar'),
    ]
    
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Additional fields for different roles
    student_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Two-factor authentication
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = AdminUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.username


class Club(models.Model):
    """Represents a student club."""
    club_number = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)
    faculty_mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='mentored_clubs'
    )
    faculty_mentor_name = models.CharField(max_length=255, blank=True, help_text="Display name of faculty mentor for this club")
    declaration_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.club_number})"


class ClubMember(models.Model):
    """Membership with role and academic details."""
    ROLE_CHOICES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('treasurer', 'Treasurer'),
        ('secretary', 'Secretary'),
        ('member', 'Member'),
        ('faculty', 'Faculty Mentor'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('revoked', 'Revoked'),
    ]

    club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='club_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    department = models.CharField(max_length=128, blank=True)
    academic_year = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_memberships'
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='revoked_memberships'
    )

    class Meta:
        unique_together = ('club', 'user', 'role')

    def __str__(self):
        return f"{self.user.username} - {self.role} @ {self.club.name}"


class RoleHistory(models.Model):
    """Audit trail for role changes."""
    ACTION_CHOICES = [
        ('requested', 'Role Requested'),
        ('approved', 'Role Approved'),
        ('revoked', 'Role Revoked'),
        ('rejected', 'Role Rejected'),
    ]

    club_member = models.ForeignKey('ClubMember', on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='role_actions_performed'
    )
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Role History'
        verbose_name_plural = 'Role Histories'

    def __str__(self):
        return f"{self.action} - {self.club_member} at {self.timestamp}"


class ApprovalRequest(models.Model):
    """
    Centralized approval system for events, budgets, and resources.
    Tracks all requests requiring administrative approval.
    """
    TYPE_CHOICES = [
        ('event', 'Event'),
        ('budget', 'Budget'),
        ('resource', 'Resource'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
    ]

    REVIEWER_ROLE_CHOICES = [
        ('faculty', 'Faculty Approved'),
        ('treasurer', 'Treasurer'),
        ('secretary', 'Secretary'),
        ('admin', 'Admin'),
    ]

    # Basic Information
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='approval_requests')
    
    # Financial Details (for budget requests)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_category = models.CharField(max_length=100, blank=True)
    
    # Event Details (for event requests)
    event_date = models.DateTimeField(null=True, blank=True)
    event_location = models.CharField(max_length=255, blank=True)
    expected_participants = models.IntegerField(null=True, blank=True)
    
    # Resource Details (for resource requests)
    resource_name = models.CharField(max_length=255, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    resource_category = models.CharField(max_length=100, blank=True)
    
    # Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_reviewer_role = models.CharField(max_length=20, choices=REVIEWER_ROLE_CHOICES, blank=True)
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    
    # Tracking
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_requests'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests'
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_requests'
    )
    
    # Attachments
    attachment_url = models.URLField(blank=True)
    supporting_documents = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Admin Notes
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'request_type']),
            models.Index(fields=['club', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.title} ({self.get_status_display()})"


class ApprovalHistory(models.Model):
    """
    Detailed audit trail for approval requests.
    Tracks every action performed on an approval request.
    """
    ACTION_CHOICES = [
        ('created', 'Request Created'),
        ('submitted', 'Submitted for Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('modified', 'Modified'),
        ('commented', 'Comment Added'),
        ('reassigned', 'Reassigned'),
    ]

    approval_request = models.ForeignKey(
        'ApprovalRequest',
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approval_actions_performed'
    )
    
    # Change tracking
    field_changed = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    # Additional context
    comment = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Approval History'
        verbose_name_plural = 'Approval Histories'

    def __str__(self):
        return f"{self.action} by {self.performed_by} at {self.timestamp}"


class Event(models.Model):
    """
    Comprehensive Event management system.
    Handles single club and joint events with full lifecycle tracking.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('closed', 'Closed'),
    ]

    EVENT_TYPE_CHOICES = [
        ('academic', 'Academic'),
        ('cultural', 'Cultural'),
        ('technical', 'Technical'),
        ('sports', 'Sports'),
        ('social', 'Social Service'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('competition', 'Competition'),
        ('fundraiser', 'Fundraiser'),
        ('other', 'Other'),
    ]

    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('members_only', 'Members Only'),
    ]

    # Basic Information
    event_id = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    
    # Primary club (always required)
    primary_club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='organized_events')
    
    # Collaborating clubs (for joint events)
    collaborating_clubs = models.ManyToManyField('Club', blank=True, related_name='joint_events')
    is_joint_event = models.BooleanField(default=False)
    
    # Date & Time
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_start = models.DateTimeField(null=True, blank=True)
    registration_end = models.DateTimeField(null=True, blank=True)
    
    # Location
    venue = models.CharField(max_length=255)
    venue_address = models.TextField(blank=True)
    is_online = models.BooleanField(default=False)
    online_meeting_link = models.URLField(blank=True)
    
    # Capacity & Registration
    max_participants = models.IntegerField(null=True, blank=True)
    current_registrations = models.IntegerField(default=0)
    requires_registration = models.BooleanField(default=False)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Budget & Finance
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2)
    approved_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_expense = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_category = models.CharField(max_length=100, blank=True)
    sponsorship_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status & Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    requires_approval = models.BooleanField(default=True)
    approval_request = models.OneToOneField(
        'ApprovalRequest',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='event_detail'
    )
    
    # People
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_events'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_events'
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_events'
    )
    
    # Contact & Coordinators
    primary_coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='coordinated_events'
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Media & Attachments
    poster_url = models.URLField(blank=True)
    banner_url = models.URLField(blank=True)
    gallery_urls = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    
    # Post-Event Data
    actual_participants = models.IntegerField(null=True, blank=True)
    feedback_collected = models.BooleanField(default=False)
    report_generated = models.BooleanField(default=False)
    report_url = models.URLField(blank=True)
    success_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Admin Controls
    featured = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['primary_club', 'status']),
            models.Index(fields=['is_joint_event']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.event_id})"

    @property
    def is_past(self):
        from django.utils import timezone
        return self.end_date < timezone.now()

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def registration_open(self):
        if not self.requires_registration:
            return False
        from django.utils import timezone
        now = timezone.now()
        if self.registration_start and self.registration_end:
            return self.registration_start <= now <= self.registration_end
        return True

    @property
    def budget_utilization(self):
        if self.approved_budget and self.actual_expense:
            return (self.actual_expense / self.approved_budget) * 100
        return 0


class EventCollaborator(models.Model):
    """
    Tracks club collaboration details for joint events.
    """
    ROLE_CHOICES = [
        ('primary', 'Primary Organizer'),
        ('co_organizer', 'Co-Organizer'),
        ('sponsor', 'Sponsor'),
        ('partner', 'Partner'),
        ('supporter', 'Supporter'),
    ]

    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('withdrawn', 'Withdrawn'),
    ]

    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='collaborations')
    club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='event_collaborations')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    
    # Contribution
    budget_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    resource_contribution = models.TextField(blank=True)
    volunteer_count = models.IntegerField(default=0)
    
    # Contact
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='collaboration_coordinator'
    )
    
    # Timestamps
    invited_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('event', 'club')

    def __str__(self):
        return f"{self.club.name} - {self.role} for {self.event.title}"


class EventLog(models.Model):
    """
    Comprehensive audit trail for events.
    Tracks all actions, changes, and important milestones.
    """
    ACTION_CHOICES = [
        ('created', 'Event Created'),
        ('updated', 'Event Updated'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Event Approved'),
        ('rejected', 'Event Rejected'),
        ('started', 'Event Started'),
        ('completed', 'Event Completed'),
        ('cancelled', 'Event Cancelled'),
        ('closed', 'Event Closed'),
        ('budget_updated', 'Budget Updated'),
        ('collaborator_added', 'Collaborator Added'),
        ('collaborator_removed', 'Collaborator Removed'),
        ('participant_registered', 'Participant Registered'),
        ('report_generated', 'Report Generated'),
    ]

    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_actions'
    )
    
    # Change tracking
    field_changed = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    # Context
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.event.title} at {self.timestamp}"


class EventReport(models.Model):
    """
    Post-event reports with detailed analytics and outcomes.
    """
    REPORT_TYPE_CHOICES = [
        ('summary', 'Event Summary'),
        ('financial', 'Financial Report'),
        ('feedback', 'Feedback Report'),
        ('attendance', 'Attendance Report'),
        ('comprehensive', 'Comprehensive Report'),
    ]

    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    
    # Summary
    title = models.CharField(max_length=255)
    summary = models.TextField()
    
    # Statistics
    total_participants = models.IntegerField(default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_variance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Outcomes
    objectives_met = models.TextField(blank=True)
    challenges_faced = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Feedback
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    feedback_count = models.IntegerField(default=0)
    feedback_summary = models.TextField(blank=True)
    
    # Media
    photos_count = models.IntegerField(default=0)
    videos_count = models.IntegerField(default=0)
    media_urls = models.JSONField(default=list, blank=True)
    
    # Files
    report_file_url = models.URLField(blank=True)
    supporting_documents = models.JSONField(default=list, blank=True)
    
    # Generation metadata
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.event.title}"


class UniversityProfile(models.Model):
    """Stores institution-wide branding, identity, and contact details."""

    name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    logo_url = models.URLField(blank=True)
    favicon_url = models.URLField(blank=True)
    hero_image_url = models.URLField(blank=True)

    primary_color = models.CharField(max_length=20, blank=True)
    secondary_color = models.CharField(max_length=20, blank=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    accreditation = models.CharField(max_length=255, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)

    storage_bucket = models.CharField(max_length=255, blank=True)
    storage_region = models.CharField(max_length=100, blank=True)
    storage_folder = models.CharField(max_length=255, blank=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_university_profiles'
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'university_profile'
        verbose_name = 'University Profile'
        verbose_name_plural = 'University Profiles'

    def __str__(self):
        return self.name

class Resource(models.Model):
    """
    University resources that can be booked by clubs and users.
    Supports both physical and digital resources.
    """
    RESOURCE_TYPE_CHOICES = [
        ('physical', 'Physical'),
        ('digital', 'Digital'),
    ]

    CATEGORY_CHOICES = [
        ('room', 'Room/Hall'),
        ('equipment', 'Equipment'),
        ('vehicle', 'Vehicle'),
        ('software', 'Software License'),
        ('hardware', 'Hardware'),
        ('lab', 'Laboratory'),
        ('sports', 'Sports Facility'),
        ('av_equipment', 'Audio/Visual Equipment'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('damaged', 'Damaged'),
    ]

    BOOKING_MODE_CHOICES = [
        ('auto', 'Auto Approval'),
        ('manual', 'Manual Approval'),
    ]

    # Basic Information
    resource_id = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    
    # Specifications
    capacity = models.IntegerField(null=True, blank=True, help_text="For rooms/halls - seating capacity")
    specifications = models.JSONField(default=dict, blank=True, help_text="Technical specs, features, etc.")
    
    # Location (for physical resources)
    location = models.CharField(max_length=255, blank=True)
    building = models.CharField(max_length=100, blank=True)
    floor = models.CharField(max_length=20, blank=True)
    room_number = models.CharField(max_length=50, blank=True)
    
    # Digital Resource Details
    access_url = models.URLField(blank=True, help_text="URL for digital resources")
    license_key = models.CharField(max_length=500, blank=True)
    concurrent_users = models.IntegerField(null=True, blank=True, help_text="Max simultaneous users")
    
    # Availability
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_bookable = models.BooleanField(default=True)
    booking_mode = models.CharField(max_length=10, choices=BOOKING_MODE_CHOICES, default='manual')
    
    # Time constraints
    min_booking_duration = models.DurationField(null=True, blank=True, help_text="Minimum booking duration")
    max_booking_duration = models.DurationField(null=True, blank=True, help_text="Maximum booking duration")
    advance_booking_days = models.IntegerField(default=30, help_text="How many days in advance can be booked")
    
    # Approval workflow
    requires_faculty_approval = models.BooleanField(default=True)
    requires_admin_approval = models.BooleanField(default=True)
    
    # Cost
    cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit_required = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Metadata
    image_url = models.URLField(blank=True)
    documents = models.JSONField(default=list, blank=True, help_text="Manuals, guidelines, etc.")
    tags = models.JSONField(default=list, blank=True)
    
    # Management
    managed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_resources'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_resources'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['resource_type', 'status']),
            models.Index(fields=['category', 'is_bookable']),
        ]

    def __str__(self):
        return f"{self.name} ({self.resource_id})"


class ResourceBooking(models.Model):
    """
    Booking records for resources with conflict detection and approval workflow.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('faculty_approved', 'Faculty Approved'),
        ('admin_approved', 'Admin Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    # Basic Information
    booking_id = models.CharField(max_length=20, unique=True, db_index=True)
    resource = models.ForeignKey('Resource', on_delete=models.CASCADE, related_name='bookings')
    
    # Booking Details
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resource_bookings'
    )
    club = models.ForeignKey('Club', null=True, blank=True, on_delete=models.SET_NULL, related_name='resource_bookings')
    
    # Time Slot
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    duration = models.DurationField()
    
    # Purpose
    purpose = models.TextField()
    event = models.ForeignKey('Event', null=True, blank=True, on_delete=models.SET_NULL, related_name='resource_bookings')
    expected_attendees = models.IntegerField(null=True, blank=True)
    
    # Status & Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval Chain
    faculty_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='faculty_approved_bookings'
    )
    faculty_approved_at = models.DateTimeField(null=True, blank=True)
    
    admin_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='admin_approved_bookings'
    )
    admin_approved_at = models.DateTimeField(null=True, blank=True)
    
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rejected_bookings'
    )
    rejection_reason = models.TextField(blank=True)
    
    # Cost & Payment
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded')],
        default='pending'
    )
    
    # Setup & Teardown
    setup_required = models.BooleanField(default=False)
    setup_notes = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    
    # Feedback & Completion
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    damage_report = models.TextField(blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['resource', 'start_time', 'end_time']),
            models.Index(fields=['status', 'start_time']),
            models.Index(fields=['booked_by', '-created_at']),
        ]

    def __str__(self):
        return f"{self.booking_id} - {self.resource.name} ({self.start_time.date()})"

    def has_conflict(self):
        """Check if this booking conflicts with existing bookings."""
        conflicting = ResourceBooking.objects.filter(
            resource=self.resource,
            status__in=['approved', 'faculty_approved', 'admin_approved', 'pending']
        ).exclude(id=self.id).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        return conflicting.exists()

    def calculate_cost(self):
        """Calculate total cost based on duration and resource rate."""
        if self.resource.cost_per_hour > 0:
            hours = self.duration.total_seconds() / 3600
            self.total_cost = float(hours) * float(self.resource.cost_per_hour)
        return self.total_cost


class ResourceLog(models.Model):
    """
    Immutable audit log for all resource-related actions.
    Records every change, access, and operation.
    """
    ACTION_CHOICES = [
        ('created', 'Resource Created'),
        ('updated', 'Resource Updated'),
        ('booking_created', 'Booking Created'),
        ('booking_approved', 'Booking Approved'),
        ('booking_rejected', 'Booking Rejected'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('maintenance_started', 'Maintenance Started'),
        ('maintenance_completed', 'Maintenance Completed'),
        ('status_changed', 'Status Changed'),
        ('damage_reported', 'Damage Reported'),
    ]

    # Log Entry
    log_id = models.CharField(max_length=20, unique=True, db_index=True)
    resource = models.ForeignKey('Resource', on_delete=models.CASCADE, related_name='logs')
    booking = models.ForeignKey('ResourceBooking', null=True, blank=True, on_delete=models.SET_NULL, related_name='logs')
    
    # Action Details
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    
    # Actor
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='resource_actions'
    )
    
    # Change Tracking
    field_changed = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamp (immutable)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Resource Log'
        verbose_name_plural = 'Resource Logs'

    def __str__(self):
        return f"{self.log_id} - {self.action} at {self.timestamp}"

    def save(self, *args, **kwargs):
        """Override save to prevent updates (immutable logs)."""
        if self.pk:
            raise ValueError("Resource logs cannot be modified once created.")
        
        # Generate log_id if not present
        if not self.log_id:
            import uuid
            self.log_id = f"LOG-{uuid.uuid4().hex[:12].upper()}"
        
        super().save(*args, **kwargs)