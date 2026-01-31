"""
Club Application Management Views
Handles all types of club applications with faculty → admin approval workflow.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_club_application_view(request):
    """
    Submit a new club application (member addition, position change, etc.).
    Requires club membership.
    """
    try:
        from .models import ClubApplication, Club, ClubMember
        from django.utils import timezone
        
        club_id = request.data.get('club_id')
        application_type = request.data.get('application_type')
        
        if not club_id or not application_type:
            return Response({
                'error': 'club_id and application_type are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify club exists
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return Response({'error': 'Club not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user is a member with appropriate permissions
        membership = ClubMember.objects.filter(
            club=club,
            user=request.user,
            status='active'
        ).first()
        
        if not membership:
            return Response({
                'error': 'You must be an active member of this club to submit applications'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create application
        application = ClubApplication.objects.create(
            application_type=application_type,
            club=club,
            submitted_by=request.user,
            title=request.data.get('title'),
            description=request.data.get('description'),
            justification=request.data.get('justification', ''),
            application_data=request.data.get('application_data', {}),
            attachments=request.data.get('attachments', []),
            supporting_documents_url=request.data.get('supporting_documents_url', ''),
            expected_impact=request.data.get('expected_impact', ''),
            deadline=request.data.get('deadline'),
            notes=request.data.get('notes', ''),
            status='pending_faculty',
        )
        
        return Response({
            'message': 'Application submitted successfully',
            'application_id': application.application_id,
            'status': 'pending_faculty',
        }, status=status.HTTP_201_CREATED)
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to submit application', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_club_applications_view(request):
    """
    Get all applications submitted by the logged-in user.
    """
    try:
        from .models import ClubApplication
        
        applications = ClubApplication.objects.filter(
            submitted_by=request.user
        ).select_related('club', 'faculty_reviewed_by', 'admin_reviewed_by').order_by('-created_at')
        
        applications_data = []
        for app in applications:
            applications_data.append({
                'id': app.id,
                'application_id': app.application_id,
                'application_type': app.application_type,
                'application_type_display': app.get_application_type_display(),
                'club': {
                    'id': app.club.id,
                    'name': app.club.name,
                },
                'title': app.title,
                'description': app.description,
                'justification': app.justification,
                'application_data': app.application_data,
                'status': app.status,
                'status_display': app.get_status_display(),
                'faculty_reviewed_at': app.faculty_reviewed_at.isoformat() if app.faculty_reviewed_at else None,
                'faculty_comments': app.faculty_comments,
                'faculty_rejection_reason': app.faculty_rejection_reason,
                'admin_reviewed_at': app.admin_reviewed_at.isoformat() if app.admin_reviewed_at else None,
                'admin_comments': app.admin_comments,
                'admin_rejection_reason': app.admin_rejection_reason,
                'implemented_at': app.implemented_at.isoformat() if app.implemented_at else None,
                'created_at': app.created_at.isoformat(),
                'deadline': app.deadline.isoformat() if app.deadline else None,
            })
        
        return Response({'applications': applications_data})
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch applications', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_faculty_club_applications_view(request):
    """
    Get all club applications pending faculty approval.
    Only accessible by faculty members.
    """
    try:
        from .models import ClubApplication, ClubMember
        
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
        
        # Get club applications pending faculty approval for faculty's clubs only
        applications = ClubApplication.objects.filter(
            status='pending_faculty',
            club_id__in=faculty_memberships
        ).select_related('club', 'submitted_by').order_by('-priority', '-created_at')
        
        applications_data = []
        for app in applications:
            # Handle submitted_by being None
            submitted_by_data = None
            if app.submitted_by:
                submitted_by_data = {
                    'id': app.submitted_by.id,
                    'name': f"{app.submitted_by.first_name} {app.submitted_by.last_name}",
                    'email': app.submitted_by.email,
                }
            
            applications_data.append({
                'id': app.id,
                'application_id': app.application_id,
                'application_type': app.application_type,
                'application_type_display': app.get_application_type_display(),
                'club': {
                    'id': app.club.id,
                    'name': app.club.name,
                },
                'title': app.title,
                'description': app.description,
                'justification': app.justification,
                'application_data': app.application_data,
                'expected_impact': app.expected_impact,
                'submitted_by': submitted_by_data,
                'created_at': app.created_at.isoformat(),
                'deadline': app.deadline.isoformat() if app.deadline else None,
                'priority': app.priority,
            })
        
        return Response({'pending_applications': applications_data})
    
    except Exception as exc:
        return Response(
            {'error': 'Failed to fetch pending applications', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def faculty_approve_club_application_view(request, application_id):
    """
    Faculty approves a club application.
    Changes status from 'pending_faculty' to 'pending_admin'.
    """
    try:
        from .models import ClubApplication, UniversityProfile
        from django.utils import timezone
        
        # Check if user is faculty
        try:
            profile = UniversityProfile.objects.get(user=request.user)
            if profile.user_role != 'faculty':
                return Response({
                    'error': 'Access denied. Faculty role required.'
                }, status=status.HTTP_403_FORBIDDEN)
        except UniversityProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        application = ClubApplication.objects.get(id=application_id)
        
        if application.status != 'pending_faculty':
            return Response({
                'error': f'Application is not pending faculty approval. Current status: {application.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        comments = request.data.get('comments', '')
        application.approve_by_faculty(request.user, comments)
        
        return Response({
            'message': 'Application approved by faculty. Now pending admin approval.',
            'application_id': application.application_id,
            'status': 'pending_admin',
        })
    
    except ClubApplication.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to approve application', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def faculty_reject_club_application_view(request, application_id):
    """
    Faculty rejects a club application.
    """
    try:
        from .models import ClubApplication, UniversityProfile
        
        # Check if user is faculty
        try:
            profile = UniversityProfile.objects.get(user=request.user)
            if profile.user_role != 'faculty':
                return Response({
                    'error': 'Access denied. Faculty role required.'
                }, status=status.HTTP_403_FORBIDDEN)
        except UniversityProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        application = ClubApplication.objects.get(id=application_id)
        
        if application.status != 'pending_faculty':
            return Response({
                'error': f'Application is not pending faculty approval. Current status: {application.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reason = request.data.get('rejection_reason', '')
        if not reason:
            return Response({
                'error': 'Rejection reason is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.reject_by_faculty(request.user, reason)
        
        return Response({
            'message': 'Application rejected by faculty.',
            'application_id': application.application_id,
            'status': 'faculty_rejected',
        })
    
    except ClubApplication.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to reject application', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_admin_club_applications_view(request):
    """
    Get all club applications pending admin approval.
    Only accessible by admin users.
    """
    try:
        # Check if user is admin using AdminUser.role
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return Response({
                'error': 'Access denied. Admin role required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # TODO: ClubApplication table needs migration
        # For now, return empty list until migrations are run
        return Response({'pending_applications': []})
    
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': 'Failed to fetch pending applications', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_approve_club_application_view(request, application_id):
    """
    Admin approves a club application.
    Application moves to 'approved' status and can be implemented.
    """
    try:
        from .models import ClubApplication, UniversityProfile
        
        # Check if user is admin
        try:
            profile = UniversityProfile.objects.get(user=request.user)
            if profile.user_role != 'admin':
                return Response({
                    'error': 'Access denied. Admin role required.'
                }, status=status.HTTP_403_FORBIDDEN)
        except UniversityProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        application = ClubApplication.objects.get(id=application_id)
        
        if application.status != 'pending_admin':
            return Response({
                'error': f'Application is not pending admin approval. Current status: {application.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        comments = request.data.get('comments', '')
        auto_implement = request.data.get('auto_implement', False)
        
        application.approve_by_admin(request.user, comments)
        
        # Auto-implement if requested (for simple applications like member additions)
        if auto_implement:
            implementation_result = implement_club_application(application, request.user)
            return Response({
                'message': 'Application approved and implemented successfully.',
                'application_id': application.application_id,
                'status': 'implemented',
                'implementation_result': implementation_result,
            })
        
        return Response({
            'message': 'Application approved by admin. Ready for implementation.',
            'application_id': application.application_id,
            'status': 'approved',
        })
    
    except ClubApplication.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to approve application', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_reject_club_application_view(request, application_id):
    """
    Admin rejects a club application.
    """
    try:
        from .models import ClubApplication, UniversityProfile
        
        # Check if user is admin
        try:
            profile = UniversityProfile.objects.get(user=request.user)
            if profile.user_role != 'admin':
                return Response({
                    'error': 'Access denied. Admin role required.'
                }, status=status.HTTP_403_FORBIDDEN)
        except UniversityProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        application = ClubApplication.objects.get(id=application_id)
        
        if application.status != 'pending_admin':
            return Response({
                'error': f'Application is not pending admin approval. Current status: {application.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reason = request.data.get('rejection_reason', '')
        if not reason:
            return Response({
                'error': 'Rejection reason is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.reject_by_admin(request.user, reason)
        
        return Response({
            'message': 'Application rejected by admin.',
            'application_id': application.application_id,
            'status': 'admin_rejected',
        })
    
    except ClubApplication.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to reject application', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def implement_club_application_view(request, application_id):
    """
    Implement an approved club application.
    Executes the requested changes (add member, change position, etc.).
    """
    try:
        from .models import ClubApplication, UniversityProfile
        
        # Check if user is admin or faculty
        try:
            profile = UniversityProfile.objects.get(user=request.user)
            if profile.user_role not in ['admin', 'faculty']:
                return Response({
                    'error': 'Access denied. Admin or Faculty role required.'
                }, status=status.HTTP_403_FORBIDDEN)
        except UniversityProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        application = ClubApplication.objects.get(id=application_id)
        
        if application.status != 'approved':
            return Response({
                'error': f'Application must be approved before implementation. Current status: {application.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = implement_club_application(application, request.user)
        
        notes = request.data.get('notes', '')
        application.mark_implemented(request.user, notes)
        
        return Response({
            'message': 'Application implemented successfully.',
            'application_id': application.application_id,
            'status': 'implemented',
            'result': result,
        })
    
    except ClubApplication.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response(
            {'error': 'Failed to implement application', 'details': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def implement_club_application(application, user):
    """
    Helper function to implement the actual changes based on application type.
    """
    from .models import ClubMember, AdminUser
    from django.utils import timezone
    
    result = {'success': False, 'message': ''}
    
    try:
        if application.application_type == 'member_addition':
            # Add new member to club
            data = application.application_data
            target_user = AdminUser.objects.get(id=data.get('target_user_id'))
            position = data.get('proposed_position', 'member')
            
            # Check if already a member
            existing = ClubMember.objects.filter(
                club=application.club,
                user=target_user
            ).first()
            
            if existing and existing.status == 'active':
                result['message'] = 'User is already an active member'
            else:
                if existing:
                    # Reactivate
                    existing.status = 'active'
                    existing.position = position
                    existing.approved_at = timezone.now()
                    existing.approved_by = user
                    existing.save()
                else:
                    # Create new membership
                    ClubMember.objects.create(
                        club=application.club,
                        user=target_user,
                        position=position,
                        status='active',
                        approved_at=timezone.now(),
                        approved_by=user
                    )
                result['success'] = True
                result['message'] = f'Successfully added {target_user.username} as {position}'
        
        elif application.application_type == 'position_change':
            # Change member position
            data = application.application_data
            target_user = AdminUser.objects.get(id=data.get('user_id'))
            new_position = data.get('new_position')
            
            member = ClubMember.objects.get(
                club=application.club,
                user=target_user,
                status='active'
            )
            
            old_position = member.position
            member.position = new_position
            member.save()
            
            result['success'] = True
            result['message'] = f'Changed {target_user.username} from {old_position} to {new_position}'
        
        elif application.application_type == 'member_removal':
            # Remove member from club
            data = application.application_data
            target_user = AdminUser.objects.get(id=data.get('target_user_id'))
            
            member = ClubMember.objects.get(
                club=application.club,
                user=target_user
            )
            
            member.status = 'removed'
            member.save()
            
            result['success'] = True
            result['message'] = f'Successfully removed {target_user.username} from club'
        
        else:
            result['message'] = f'Implementation not automated for {application.get_application_type_display()}. Manual action required.'
    
    except Exception as e:
        result['success'] = False
        result['message'] = f'Implementation failed: {str(e)}'
    
    return result
