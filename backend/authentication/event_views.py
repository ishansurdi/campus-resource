"""
Event Management Views
Comprehensive API endpoints for event browsing, registration, attendance tracking, and expense management.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def events_list_view(request):
    """
    Get events with filtering by status (upcoming/ongoing/past), club, department, and joint events.
    Query params: status, club_id, is_joint, search
    """
    try:
        from .models import Event
        from django.utils import timezone
        from django.db.models import Q
        
        events = Event.objects.filter(
            visibility='public',
            status__in=['approved', 'in_progress', 'completed']
        ).select_related('primary_club').prefetch_related('collaborating_clubs')
        
        # Filter by status (upcoming/ongoing/past)
        status_filter = request.GET.get('status', 'all')
        now = timezone.now()
        
        if status_filter == 'upcoming':
            events = events.filter(start_date__gt=now)
        elif status_filter == 'ongoing':
            events = events.filter(start_date__lte=now, end_date__gte=now)
        elif status_filter == 'past':
            events = events.filter(end_date__lt=now)
        
        # Filter by club
        club_id = request.GET.get('club_id')
        if club_id:
            events = events.filter(Q(primary_club_id=club_id) | Q(collaborating_clubs__id=club_id))
        
        # Filter by joint events
        is_joint = request.GET.get('is_joint')
        if is_joint == 'true':
            events = events.filter(is_joint_event=True)
        elif is_joint == 'false':
            events = events.filter(is_joint_event=False)
        
        # Search
        search = request.GET.get('search', '').strip()
        if search:
            events = events.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(event_type__icontains=search)
            )
        
        events = events.distinct().order_by('-start_date')[:100]
        
        events_data = []
        for event in events:
            collab_clubs = list(event.collaborating_clubs.values('id', 'name'))
            events_data.append({
                'id': event.id,
                'event_id': event.event_id,
                'title': event.title,
                'description': event.description[:200],  # Truncate
                'event_type': event.event_type,
                'primary_club': {
                    'id': event.primary_club.id,
                    'name': event.primary_club.name,
                },
                'collaborating_clubs': collab_clubs,
                'is_joint_event': event.is_joint_event,
                'start_date': event.start_date,
                'end_date': event.end_date,
                'venue': event.venue,
                'is_online': event.is_online,
                'online_meeting_link': event.online_meeting_link if event.is_online else None,
                'poster_url': event.poster_url,
                'requires_registration': event.requires_registration,
                'registration_fee': float(event.registration_fee) if event.registration_fee else 0,
                'max_participants': event.max_participants,
                'current_registrations': event.current_registrations,
                'status': event.status,
                'registration_open': event.registration_open,
                'is_past': event.is_past,
                'is_upcoming': event.is_upcoming,
                'is_ongoing': event.is_ongoing,
            })
        
        return Response(events_data, status=status.HTTP_200_OK)
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch events', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_detail_view(request, event_id):
    """Get detailed information about a specific event."""
    try:
        from .models import Event, EventRegistration
        
        event = Event.objects.select_related('primary_club', 'primary_coordinator').prefetch_related('collaborating_clubs').get(id=event_id)
        
        # Check if user is registered
        is_registered = EventRegistration.objects.filter(event=event, user=request.user).exists()
        user_registration = None
        if is_registered:
            reg = EventRegistration.objects.get(event=event, user=request.user)
            user_registration = {
                'registration_number': reg.registration_number,
                'status': reg.status,
                'payment_status': reg.payment_status,
                'registered_at': reg.registered_at,
            }
        
        collab_clubs = list(event.collaborating_clubs.values('id', 'name', 'club_number'))
        
        event_data = {
            'id': event.id,
            'event_id': event.event_id,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type,
            'primary_club': {
                'id': event.primary_club.id,
                'name': event.primary_club.name,
                'club_number': event.primary_club.club_number,
            },
            'collaborating_clubs': collab_clubs,
            'is_joint_event': event.is_joint_event,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'registration_start': event.registration_start,
            'registration_end': event.registration_end,
            'venue': event.venue,
            'venue_address': event.venue_address,
            'is_online': event.is_online,
            'online_meeting_link': event.online_meeting_link if event.is_online else None,
            'max_participants': event.max_participants,
            'current_registrations': event.current_registrations,
            'requires_registration': event.requires_registration,
            'registration_fee': float(event.registration_fee) if event.registration_fee else 0,
            'contact_email': event.contact_email,
            'contact_phone': event.contact_phone,
            'primary_coordinator': event.primary_coordinator.get_full_name() if event.primary_coordinator else None,
            'poster_url': event.poster_url,
            'banner_url': event.banner_url,
            'gallery_urls': event.gallery_urls,
            'status': event.status,
            'registration_open': event.registration_open,
            'is_past': event.is_past,
            'is_upcoming': event.is_upcoming,
            'is_ongoing': event.is_ongoing,
            'tags': event.tags,
            'created_at': event.created_at,
            'is_registered': is_registered,
            'user_registration': user_registration,
            'estimated_budget': float(event.estimated_budget) if event.estimated_budget else 0,
            'approved_budget': float(event.approved_budget) if event.approved_budget else 0,
            'actual_expense': float(event.actual_expense) if event.actual_expense else 0,
        }
        
        return Response(event_data, status=status.HTTP_200_OK)
    
    except Event.DoesNotExist:
        return Response(
            {'error': 'Event not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch event details', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event_registrations_view(request):
    """
    GET: List user's event registrations
    POST: Register for an event
    """
    if request.method == 'GET':
        try:
            from .models import EventRegistration
            
            registrations = EventRegistration.objects.filter(
                user=request.user
            ).select_related('event', 'event__primary_club').order_by('-registered_at')
            
            reg_data = []
            for reg in registrations:
                reg_data.append({
                    'id': reg.id,
                    'registration_number': reg.registration_number,
                    'event': {
                        'id': reg.event.id,
                        'event_id': reg.event.event_id,
                        'title': reg.event.title,
                        'start_date': reg.event.start_date,
                        'end_date': reg.event.end_date,
                        'venue': reg.event.venue,
                        'poster_url': reg.event.poster_url,
                        'is_past': reg.event.is_past,
                        'is_upcoming': reg.event.is_upcoming,
                        'is_ongoing': reg.event.is_ongoing,
                    },
                    'status': reg.status,
                    'payment_status': reg.payment_status,
                    'payment_amount': float(reg.payment_amount),
                    'registered_at': reg.registered_at,
                    'confirmed_at': reg.confirmed_at,
                })
            
            return Response(reg_data, status=status.HTTP_200_OK)
        
        except Exception as exc:
            return Response(
                {'error': 'Failed to fetch registrations', 'details': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            from .models import Event, EventRegistration
            from django.utils import timezone
            import random
            
            event_id = request.data.get('event_id')
            special_requirements = request.data.get('special_requirements', '')
            team_name = request.data.get('team_name', '')
            team_members = request.data.get('team_members', [])
            
            if not event_id:
                return Response({'error': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            event = Event.objects.get(id=event_id)
            
            # Check if event registration is open
            if not event.requires_registration:
                return Response({'error': 'This event does not require registration'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not event.registration_open:
                return Response({'error': 'Registration is closed for this event'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already registered
            if EventRegistration.objects.filter(event=event, user=request.user).exists():
                return Response({'error': 'You are already registered for this event'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check capacity
            if event.max_participants and event.current_registrations >= event.max_participants:
                return Response({'error': 'Event is full'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate registration number
            reg_number = f"EVT{event.event_id}{random.randint(1000, 9999)}"
            
            # Create registration
            registration = EventRegistration.objects.create(
                event=event,
                user=request.user,
                registration_number=reg_number,
                status='confirmed' if event.registration_fee == 0 else 'pending',
                payment_amount=event.registration_fee,
                payment_status='waived' if event.registration_fee == 0 else 'pending',
                special_requirements=special_requirements,
                team_name=team_name,
                team_members=team_members,
                confirmed_at=timezone.now() if event.registration_fee == 0 else None,
            )
            
            # Update event registration count
            event.current_registrations += 1
            event.save()
            
            return Response({
                'message': 'Successfully registered for the event',
                'registration_number': registration.registration_number,
                'status': registration.status,
            }, status=status.HTTP_201_CREATED)
        
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response(
                {'error': 'Failed to register for event', 'details': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_event_attendances_view(request):
    """Get user's event attendance records with certificate status."""
    try:
        from .models import EventAttendance, EventCertificate
        
        attendances = EventAttendance.objects.filter(
            user=request.user
        ).select_related('event', 'event__primary_club').order_by('-check_in_time')
        
        attendance_data = []
        for att in attendances:
            # Check for certificate
            certificate = None
            try:
                cert = EventCertificate.objects.get(event=att.event, user=request.user)
                certificate = {
                    'id': cert.id,
                    'certificate_id': cert.certificate_id,
                    'type': cert.certificate_type,
                    'status': cert.status,
                    'certificate_url': cert.certificate_url,
                    'issued_at': cert.issued_at,
                }
            except EventCertificate.DoesNotExist:
                pass
            
            attendance_data.append({
                'id': att.id,
                'event': {
                    'id': att.event.id,
                    'event_id': att.event.event_id,
                    'title': att.event.title,
                    'start_date': att.event.start_date,
                    'end_date': att.event.end_date,
                    'primary_club_name': att.event.primary_club.name,
                },
                'status': att.status,
                'check_in_time': att.check_in_time,
                'check_out_time': att.check_out_time,
                'duration_minutes': att.duration_minutes,
                'feedback_rating': att.feedback_rating,
                'certificate_eligible': att.certificate_eligible,
                'certificate_issued': att.certificate_issued,
                'certificate': certificate,
            })
        
        return Response(attendance_data, status=status.HTTP_200_OK)
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch attendance records', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_event_feedback_view(request, attendance_id):
    """Submit feedback and rating for an attended event."""
    try:
        from .models import EventAttendance
        from django.utils import timezone
        
        attendance = EventAttendance.objects.get(id=attendance_id, user=request.user)
        
        rating = request.data.get('rating')
        feedback_text = request.data.get('feedback', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance.feedback_rating = rating
        attendance.feedback_text = feedback_text
        attendance.feedback_submitted_at = timezone.now()
        attendance.save()
        
        return Response({'message': 'Feedback submitted successfully'}, status=status.HTTP_200_OK)
    
    except EventAttendance.DoesNotExist:
        return Response({'error': 'Attendance record not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to submit feedback', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_certificates_view(request):
    """Get all certificates earned by the user."""
    try:
        from .models import EventCertificate
        
        certificates = EventCertificate.objects.filter(
            user=request.user,
            status__in=['generated', 'issued', 'downloaded']
        ).select_related('event').order_by('-issued_at')
        
        cert_data = []
        for cert in certificates:
            cert_data.append({
                'id': cert.id,
                'certificate_id': cert.certificate_id,
                'event_title': cert.event.title,
                'event_id': cert.event.event_id,
                'certificate_type': cert.certificate_type,
                'title': cert.title,
                'description': cert.description,
                'achievement_details': cert.achievement_details,
                'certificate_url': cert.certificate_url,
                'verification_url': cert.verification_url,
                'qr_code_url': cert.qr_code_url,
                'issued_at': cert.issued_at,
                'status': cert.status,
            })
        
        return Response(cert_data, status=status.HTTP_200_OK)
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch certificates', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ================ EVENT MANAGEMENT (For Club Admins) ================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_expenses_view(request, event_id):
    """Get all expenses for an event (for event organizers and registered participants)."""
    try:
        from .models import Event, EventExpense, ClubMember, EventRegistration
        
        event = Event.objects.get(id=event_id)
        
        # Check if user is authorized (club member, event creator, or registered participant)
        is_authorized = (
            ClubMember.objects.filter(club=event.primary_club, user=request.user, status='active').exists() or
            event.created_by == request.user or
            EventRegistration.objects.filter(event=event, user=request.user).exists()
        )
        
        if not is_authorized:
            return Response({'error': 'Unauthorized. You must be a club member, event creator, or registered participant to view expenses.'}, status=status.HTTP_403_FORBIDDEN)
        
        expenses = EventExpense.objects.filter(event=event).order_by('-created_at')
        
        expense_data = []
        total_amount = 0
        for expense in expenses:
            expense_data.append({
                'id': expense.id,
                'expense_id': expense.expense_id,
                'category': expense.category,
                'title': expense.title,
                'description': expense.description,
                'amount': float(expense.amount),
                'gst_amount': float(expense.gst_amount),
                'total_amount': float(expense.total_amount),
                'payment_mode': expense.payment_mode,
                'payment_reference': expense.payment_reference,
                'payment_date': expense.payment_date,
                'paid_to': expense.paid_to,
                'paid_to_contact': expense.paid_to_contact,
                'invoice_number': expense.invoice_number,
                'invoice_date': expense.invoice_date,
                'bill_image_url': expense.bill_image_url,
                'ocr_processed': expense.ocr_processed,
                'ocr_verified': expense.ocr_verified,
                'status': expense.status,
                'notes': expense.notes,
                'created_at': expense.created_at,
            })
            if expense.status in ['approved', 'paid', 'reimbursed']:
                total_amount += expense.total_amount
        
        return Response({
            'expenses': expense_data,
            'total_expenses': float(total_amount),
            'approved_budget': float(event.approved_budget) if event.approved_budget else 0,
            'budget_utilization': event.budget_utilization,
        }, status=status.HTTP_200_OK)
    
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch expenses', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_event_expense_view(request, event_id):
    """Add a new expense entry for an event."""
    try:
        from .models import Event, EventExpense, ClubMember
        import random
        
        event = Event.objects.get(id=event_id)
        
        # Check authorization - only club members can add expenses
        is_authorized = (
            ClubMember.objects.filter(club=event.primary_club, user=request.user, status='active').exists() or
            event.created_by == request.user
        )
        
        if not is_authorized:
            return Response({'error': 'Unauthorized. Only club members can add expenses.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Generate expense ID
        expense_id = f"EXP{event.event_id}{random.randint(1000, 9999)}"
        
        # Create expense
        expense = EventExpense.objects.create(
            event=event,
            expense_id=expense_id,
            category=request.data.get('category'),
            title=request.data.get('title'),
            description=request.data.get('description', ''),
            amount=request.data.get('amount'),
            gst_amount=request.data.get('gst_amount', 0),
            total_amount=request.data.get('total_amount'),
            payment_mode=request.data.get('payment_mode', ''),
            payment_reference=request.data.get('payment_reference', ''),
            payment_date=request.data.get('payment_date'),
            paid_to=request.data.get('paid_to'),
            paid_to_contact=request.data.get('paid_to_contact', ''),
            invoice_number=request.data.get('invoice_number', ''),
            invoice_date=request.data.get('invoice_date'),
            bill_image_url=request.data.get('bill_image_url', ''),
            notes=request.data.get('notes', ''),
            submitted_by=request.user,
            status=request.data.get('status', 'pending'),
        )
        
        return Response({
            'message': 'Expense added successfully',
            'expense_id': expense.expense_id,
        }, status=status.HTTP_201_CREATED)
    
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to add expense', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_event_application_view(request):
    """
    Submit a new event application with in-depth details.
    Creates event with status='draft' initially, then changes to 'pending_faculty_approval' on submit.
    """
    try:
        from .models import Event, Club, ClubMember
        from django.utils import timezone
        import random
        import string
        
        # Check if user is a member of the club
        club_id = request.data.get('club_id')
        if not club_id:
            return Response({'error': 'Club ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return Response({'error': 'Club not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user is a member of the club
        is_member = ClubMember.objects.filter(
            club=club,
            user=request.user,
            status='active'
        ).exists()
        
        if not is_member:
            return Response({
                'error': 'You must be an active member of the club to submit event applications'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate unique event_id
        event_id = f"EVT{timezone.now().strftime('%Y%m%d')}{''.join(random.choices(string.digits, k=4))}"
        
        # Create event with detailed information
        event = Event.objects.create(
            event_id=event_id,
            title=request.data.get('title'),
            description=request.data.get('description'),
            event_type=request.data.get('event_type'),
            primary_club=club,
            is_joint_event=request.data.get('is_joint_event', False),
            
            # Date & Time
            start_date=request.data.get('start_date'),
            end_date=request.data.get('end_date'),
            registration_start=request.data.get('registration_start'),
            registration_end=request.data.get('registration_end'),
            
            # Location
            venue=request.data.get('venue'),
            venue_address=request.data.get('venue_address', ''),
            is_online=request.data.get('is_online', False),
            online_meeting_link=request.data.get('online_meeting_link', ''),
            
            # Capacity & Registration
            max_participants=request.data.get('max_participants'),
            requires_registration=request.data.get('requires_registration', False),
            registration_fee=request.data.get('registration_fee', 0),
            
            # Budget
            estimated_budget=request.data.get('estimated_budget'),
            budget_breakdown=request.data.get('budget_breakdown', {}),
            funding_source=request.data.get('funding_source', ''),
            sponsorship_amount=request.data.get('sponsorship_amount', 0),
            
            # Application Details
            objectives=request.data.get('objectives', ''),
            target_audience=request.data.get('target_audience', ''),
            expected_outcomes=request.data.get('expected_outcomes', ''),
            safety_measures=request.data.get('safety_measures', ''),
            resource_requirements=request.data.get('resource_requirements', ''),
            volunteer_requirements=request.data.get('volunteer_requirements', ''),
            special_permissions=request.data.get('special_permissions', ''),
            risk_assessment=request.data.get('risk_assessment', ''),
            
            # Faculty Mentor
            faculty_mentor_name=request.data.get('faculty_mentor_name'),
            faculty_mentor_email=request.data.get('faculty_mentor_email', ''),
            faculty_mentor_department=request.data.get('faculty_mentor_department', ''),
            
            # Contact
            primary_coordinator=request.user,
            contact_email=request.data.get('contact_email', request.user.email),
            contact_phone=request.data.get('contact_phone', ''),
            
            # Media
            poster_url=request.data.get('poster_url', ''),
            banner_url=request.data.get('banner_url', ''),
            
            # Status
            status='pending_faculty_approval',
            visibility=request.data.get('visibility', 'public'),
            created_by=request.user,
        )
        
        # Add collaborating clubs if joint event
        collaborating_club_ids = request.data.get('collaborating_clubs', [])
        if collaborating_club_ids:
            event.collaborating_clubs.set(collaborating_club_ids)
        
        # Log the creation
        from .models import EventLog
        EventLog.objects.create(
            event=event,
            action='submitted',
            performed_by=request.user,
            description='Event application submitted for faculty approval',
        )
        
        return Response({
            'message': 'Event application submitted successfully',
            'event_id': event.event_id,
            'status': 'pending_faculty_approval',
        }, status=status.HTTP_201_CREATED)
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to submit event application', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_event_applications_view(request):
    """
    Get all event applications created by the logged-in user.
    Includes pending, approved, and rejected applications.
    """
    try:
        from .models import Event
        
        events = Event.objects.filter(created_by=request.user).select_related(
            'primary_club',
            'faculty_approved_by',
            'admin_approved_by'
        ).order_by('-created_at')
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'event_id': event.event_id,
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'club': {
                    'id': event.primary_club.id,
                    'name': event.primary_club.name,
                },
                'status': event.status,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat(),
                'venue': event.venue,
                'estimated_budget': str(event.estimated_budget),
                'faculty_mentor_name': event.faculty_mentor_name,
                'faculty_approved_at': event.faculty_approved_at.isoformat() if event.faculty_approved_at else None,
                'faculty_rejection_reason': event.faculty_rejection_reason,
                'admin_approved_at': event.admin_approved_at.isoformat() if event.admin_approved_at else None,
                'admin_rejection_reason': event.admin_rejection_reason,
                'created_at': event.created_at.isoformat(),
            })
        
        return Response({'applications': events_data})
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch applications', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_faculty_approvals_view(request):
    """
    Get all events pending faculty approval.
    Only accessible by faculty members (users with role='faculty').
    """
    try:
        from .models import Event, ClubMember
        
        # Check if user is faculty - must be a faculty member of at least one club
        faculty_memberships = ClubMember.objects.filter(
            user=request.user,
            role='faculty',
            status='active'
        ).values_list('club_id', flat=True)
        
        if not faculty_memberships:
            return Response({
                'error': 'Access denied. Faculty role required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get events pending faculty approval for faculty's clubs only
        events = Event.objects.filter(
            status='pending_faculty_approval',
            primary_club_id__in=faculty_memberships
        ).select_related('primary_club', 'created_by').prefetch_related('collaborating_clubs').order_by('-created_at')
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'event_id': event.event_id,
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'club': {
                    'id': event.primary_club.id,
                    'name': event.primary_club.name,
                },
                'is_joint_event': event.is_joint_event,
                'collaborating_clubs': [{'id': c.id, 'name': c.name} for c in event.collaborating_clubs.all()],
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat(),
                'venue': event.venue,
                'max_participants': event.max_participants,
                'estimated_budget': str(event.estimated_budget),
                'budget_breakdown': event.budget_breakdown,
                'funding_source': event.funding_source,
                'objectives': event.objectives,
                'target_audience': event.target_audience,
                'expected_outcomes': event.expected_outcomes,
                'safety_measures': event.safety_measures,
                'resource_requirements': event.resource_requirements,
                'volunteer_requirements': event.volunteer_requirements,
                'special_permissions': event.special_permissions,
                'risk_assessment': event.risk_assessment,
                'faculty_mentor_name': event.faculty_mentor_name,
                'faculty_mentor_email': event.faculty_mentor_email,
                'faculty_mentor_department': event.faculty_mentor_department,
                'created_by': {
                    'id': event.created_by.id,
                    'name': f"{event.created_by.first_name} {event.created_by.last_name}",
                    'email': event.created_by.email,
                },
                'created_at': event.created_at.isoformat(),
            })
        
        return Response({'pending_events': events_data})
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch pending approvals', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def faculty_approve_event_view(request, event_id):
    """
    Faculty approves an event application.
    Changes status from 'pending_faculty_approval' to 'pending_admin_approval'.
    """
    try:
        from .models import Event, ClubMember, EventLog
        from django.utils import timezone
        
        # Check if user is faculty - must be a faculty member of at least one club
        faculty_memberships = ClubMember.objects.filter(
            user=request.user,
            role='faculty',
            status='active'
        ).values_list('club_id', flat=True)
        
        if not faculty_memberships:
            return Response({
                'error': 'Access denied. Faculty role required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get event
        event = Event.objects.get(id=event_id)
        
        # Verify event belongs to one of faculty's clubs
        if event.primary_club_id not in faculty_memberships:
            return Response({
                'error': 'Access denied. You can only approve events from your clubs.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if event.status != 'pending_faculty_approval':
            return Response({
                'error': f'Event is not pending faculty approval. Current status: {event.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Approve
        event.status = 'pending_admin_approval'
        event.faculty_approved_by = request.user
        event.faculty_approved_at = timezone.now()
        event.save()
        
        # Log the approval
        EventLog.objects.create(
            event=event,
            action='approved',
            performed_by=request.user,
            description='Event application approved by faculty',
            metadata={'approval_stage': 'faculty'},
        )
        
        return Response({
            'message': 'Event approved by faculty. Now pending admin approval.',
            'event_id': event.event_id,
            'status': 'pending_admin_approval',
        })
    
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to approve event', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def faculty_reject_event_view(request, event_id):
    """
    Faculty rejects an event application.
    Changes status from 'pending_faculty_approval' to 'faculty_rejected'.
    """
    try:
        from .models import Event, ClubMember, EventLog
        from django.utils import timezone
        
        # Check if user is faculty - must be a faculty member of at least one club
        faculty_memberships = ClubMember.objects.filter(
            user=request.user,
            role='faculty',
            status='active'
        ).values_list('club_id', flat=True)
        
        if not faculty_memberships:
            return Response({
                'error': 'Access denied. Faculty role required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get event
        event = Event.objects.get(id=event_id)
        
        # Verify event belongs to one of faculty's clubs
        if event.primary_club_id not in faculty_memberships:
            return Response({
                'error': 'Access denied. You can only reject events from your clubs.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if event.status != 'pending_faculty_approval':
            return Response({
                'error': f'Event is not pending faculty approval. Current status: {event.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rejection_reason = request.data.get('rejection_reason', '')
        if not rejection_reason:
            return Response({
                'error': 'Rejection reason is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reject
        event.status = 'faculty_rejected'
        event.faculty_approved_by = request.user
        event.faculty_approved_at = timezone.now()
        event.faculty_rejection_reason = rejection_reason
        event.save()
        
        # Log the rejection
        EventLog.objects.create(
            event=event,
            action='rejected',
            performed_by=request.user,
            description=f'Event application rejected by faculty: {rejection_reason}',
            metadata={'approval_stage': 'faculty'},
        )
        
        return Response({
            'message': 'Event rejected by faculty.',
            'event_id': event.event_id,
            'status': 'faculty_rejected',
        })
    
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to reject event', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_admin_approvals_view(request):
    """
    Get all events pending admin approval.
    Only accessible by admin users (users with role='admin').
    """
    try:
        from .models import Event
        
        # Check if user is admin using AdminUser.role
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return Response({
                'error': 'Access denied. Admin role required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get events pending admin approval
        events = Event.objects.filter(
            status='pending_admin_approval'
        ).select_related(
            'primary_club',
            'created_by',
            'faculty_approved_by'
        ).prefetch_related('collaborating_clubs').order_by('-faculty_approved_at')
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'event_id': event.event_id,
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'club': {
                    'id': event.primary_club.id,
                    'name': event.primary_club.name,
                },
                'is_joint_event': event.is_joint_event,
                'collaborating_clubs': [{'id': c.id, 'name': c.name} for c in event.collaborating_clubs.all()],
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat(),
                'venue': event.venue,
                'max_participants': event.max_participants,
                'estimated_budget': str(event.estimated_budget),
                'budget_breakdown': event.budget_breakdown,
                'funding_source': event.funding_source,
                'objectives': event.objectives,
                'target_audience': event.target_audience,
                'expected_outcomes': event.expected_outcomes,
                'safety_measures': event.safety_measures,
                'resource_requirements': event.resource_requirements,
                'volunteer_requirements': event.volunteer_requirements,
                'special_permissions': event.special_permissions,
                'risk_assessment': event.risk_assessment,
                'faculty_mentor_name': event.faculty_mentor_name,
                'faculty_approved_by': {
                    'id': event.faculty_approved_by.id if event.faculty_approved_by else None,
                    'name': f"{event.faculty_approved_by.first_name} {event.faculty_approved_by.last_name}" if event.faculty_approved_by else None,
                },
                'faculty_approved_at': event.faculty_approved_at.isoformat() if event.faculty_approved_at else None,
                'created_by': {
                    'id': event.created_by.id,
                    'name': f"{event.created_by.first_name} {event.created_by.last_name}",
                    'email': event.created_by.email,
                },
                'created_at': event.created_at.isoformat(),
            })
        
        return Response({'pending_events': events_data})
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch pending approvals', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def admin_approve_event_view(request, event_id):
    """
    Admin approves an event application.
    Changes status from 'pending_admin_approval' to 'approved'.
    Event becomes active and visible to all users.
    """
    try:
        from .models import Event, AdminUser, EventLog
        from django.utils import timezone
        import traceback
        
        print(f"Admin approve called for event_id: {event_id}")
        print(f"Request user: {request.user}")
        
        # Check if user is admin (request.user IS an AdminUser instance)
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            print(f"Access denied. User role: {getattr(request.user, 'role', 'no role attr')}")
            return Response({
                'error': 'Access denied. Admin role required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"Admin user: {request.user.email}, role: {request.user.role}")
        
        # Get event
        event = Event.objects.get(id=event_id)
        print(f"Event found: {event.event_id}, status: {event.status}")
        
        if event.status != 'pending_admin_approval':
            return Response({
                'error': f'Event is not pending admin approval. Current status: {event.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Approve
        approved_budget = request.data.get('approved_budget', event.estimated_budget)
        print(f"Approving with budget: {approved_budget}")
        
        event.status = 'approved'
        event.admin_approved_by = request.user
        event.admin_approved_at = timezone.now()
        event.approved_by = request.user  # Legacy field
        event.approved_at = timezone.now()
        event.approved_budget = approved_budget
        event.save()
        print("Event saved successfully")
        
        # Log the approval
        EventLog.objects.create(
            event=event,
            action='approved',
            performed_by=request.user,
            description='Event application approved by admin. Event is now active.',
            metadata={
                'approval_stage': 'admin',
                'approved_budget': str(approved_budget),
            },
        )
        print("Event log created")
        
        return Response({
            'message': 'Event approved by admin. Event is now active and visible to all users.',
            'event_id': event.event_id,
            'status': 'approved',
        })
    
    except Event.DoesNotExist:
        print(f"Event {event_id} not found")
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        print(f"Error approving event: {str(exc)}")
        traceback.print_exc()
        return Response(
            {'error': 'Failed to approve event', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def admin_reject_event_view(request, event_id):
    """
    Admin rejects an event application.
    Changes status from 'pending_admin_approval' to 'admin_rejected'.
    """
    try:
        from .models import Event, AdminUser, EventLog
        from django.utils import timezone
        import traceback
        
        print(f"Admin reject called for event_id: {event_id}")
        
        # Check if user is admin (request.user IS an AdminUser instance)
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            print(f"Access denied. User role: {getattr(request.user, 'role', 'no role attr')}")
            return Response({
                'error': 'Access denied. Admin role required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"Admin user: {request.user.email}, role: {request.user.role}")
        
        # Get event
        event = Event.objects.get(id=event_id)
        
        if event.status != 'pending_admin_approval':
            return Response({
                'error': f'Event is not pending admin approval. Current status: {event.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rejection_reason = request.data.get('rejection_reason', '')
        if not rejection_reason:
            return Response({
                'error': 'Rejection reason is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reject
        event.status = 'admin_rejected'
        event.admin_approved_by = request.user
        event.admin_approved_at = timezone.now()
        event.admin_rejection_reason = rejection_reason
        event.save()
        
        # Log the rejection
        EventLog.objects.create(
            event=event,
            action='rejected',
            performed_by=request.user,
            description=f'Event application rejected by admin: {rejection_reason}',
            metadata={'approval_stage': 'admin'},
        )
        
        return Response({
            'message': 'Event rejected by admin.',
            'event_id': event.event_id,
            'status': 'admin_rejected',
        })
    
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to reject event', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

