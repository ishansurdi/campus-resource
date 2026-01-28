from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
import uuid
import boto3
from .models import AdminUser, UniversityProfile
from .models import Club, ClubMember, RoleHistory, ApprovalRequest, ApprovalHistory
from .serializers import (
    AdminUserSerializer, 
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    RegisterSerializer,
    UniversityProfileSerializer,
    ClubSerializer, ClubMemberDetailSerializer, RoleHistorySerializer,
    ApprovalRequestSerializer, ApprovalRequestCreateSerializer, ApprovalHistorySerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with additional user data."""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint for all user roles.
    Returns JWT tokens and user data.
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid input', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    role = serializer.validated_data.get('role')
    two_factor_code = serializer.validated_data.get('two_factor_code')
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check role if specified
    if role and user.role != role:
        return Response(
            {'error': f'User is not authorized as {role}'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check two-factor authentication for admin
    if user.role == 'admin' and user.two_factor_enabled:
        if not two_factor_code:
            return Response(
                {'error': 'Two-factor authentication code required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # TODO: Implement actual 2FA verification
        # For now, we'll skip the actual verification
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['username'] = user.username
    refresh['role'] = user.role
    refresh['email'] = user.email
    
    return Response({
        'message': 'Login successful',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': AdminUserSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Registration endpoint for new users.
    """
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid input', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = serializer.save()
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Registration successful',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': AdminUserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint - blacklists the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response(
            {'message': 'Logout successful'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    Get current user profile.
    """
    serializer = AdminUserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user profile.
    """
    serializer = AdminUserSerializer(
        request.user, 
        data=request.data, 
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(
        {'error': 'Invalid input', 'details': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint.
    """
    return Response({
        'status': 'healthy',
        'message': 'CAMPUSPHERE API is operational'
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([AllowAny])
def university_profile_view(request):
    """Get or update global university profile. Public GET, admin updates."""

    profile, _ = UniversityProfile.objects.get_or_create(
        pk=1,
        defaults={
            'name': 'Your University',
            'tagline': 'Excellence in Education'
        }
    )

    # Allow anyone to read; restrict writes to admin role
    if request.method in ['PUT', 'PATCH']:
        if not request.user.is_authenticated or getattr(request.user, 'role', '') != 'admin':
            return Response({'error': 'Admin privileges required'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UniversityProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid input', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UniversityProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def university_upload_view(request):
    """Upload branding assets to S3. Admin only."""
    try:
        print(f"Upload request received from user: {request.user.username}, role: {request.user.role}")
        
        if getattr(request.user, 'role', '') != 'admin':
            return Response({'error': 'Admin privileges required'}, status=status.HTTP_403_FORBIDDEN)

        file_obj = request.FILES.get('file')
        folder = request.data.get('folder', 'branding')
        
        print(f"File: {file_obj.name if file_obj else 'None'}, Folder: {folder}")
        
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Get AWS settings from Django settings
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        region = getattr(settings, 'AWS_S3_REGION_NAME', '')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')

        print(f"AWS Config - Bucket: {bucket}, Region: {region}, Has Key: {bool(access_key)}, Has Secret: {bool(secret_key)}")

        if not bucket or not region or not access_key or not secret_key:
            return Response({
                'error': 'AWS configuration missing',
                'details': f'Bucket: {bool(bucket)}, Region: {bool(region)}, Key: {bool(access_key)}, Secret: {bool(secret_key)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        print("Initializing S3 client...")
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        # Generate unique filename
        key = f"{folder.strip('/')}/{uuid.uuid4()}_{file_obj.name}"
        print(f"Generated S3 key: {key}")
        
        print("Uploading to S3...")
        # Upload to S3 (without ACL since bucket may have ACLs disabled)
        s3_client.upload_fileobj(
            file_obj,
            bucket,
            key,
            ExtraArgs={
                'ContentType': file_obj.content_type or 'application/octet-stream'
            }
        )
        
        print("Upload successful!")
        # Return public URL
        url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        return Response({
            'url': url, 
            'key': key,
            'message': 'File uploaded successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as exc:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Upload error: {error_trace}")
        return Response({
            'error': 'Upload failed',
            'details': str(exc),
            'traceback': error_trace if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def clubs_view(request):
    """List all clubs or create a new club (admin only)."""
    if request.method == 'GET':
        clubs = Club.objects.all().order_by('-created_at')
        # Prepare S3 client for presigned URLs
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        region = settings.AWS_S3_REGION_NAME
        access_key = settings.AWS_ACCESS_KEY_ID
        secret_key = settings.AWS_SECRET_ACCESS_KEY
        s3_client = None
        if bucket and region and access_key and secret_key:
            try:
                s3_client = boto3.client(
                    's3',
                    region_name=region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
            except Exception:
                s3_client = None
        payload = []
        for c in clubs:
            # Generate presigned URL if object is private
            dec_url = c.declaration_url
            if s3_client and dec_url:
                prefix = f"https://{bucket}.s3.{region}.amazonaws.com/"
                if dec_url.startswith(prefix):
                    key = dec_url[len(prefix):]
                    try:
                        dec_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': bucket, 'Key': key},
                            ExpiresIn=86400
                        )
                    except Exception:
                        pass
            payload.append({
                'id': c.id,
                'club_number': c.club_number,
                'name': c.name,
                'faculty_mentor': c.faculty_mentor_name or (c.faculty_mentor.get_full_name() if c.faculty_mentor else None),
                'declaration_url': dec_url,
                'members': [
                    {
                        'username': m.user.username,
                        'email': m.user.email,
                        'role': m.role,
                        'department': m.department,
                        'academic_year': m.academic_year,
                    } for m in c.members.all()
                ]
            })
        return Response(payload, status=status.HTTP_200_OK)

    # POST - create club
    if getattr(request.user, 'role', '') != 'admin':
        return Response({'error': 'Admin privileges required'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ClubSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': 'Invalid input', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Create or get users for members
    import secrets
    created_users = []
    faculty_user = None
    try:
        for member in data['members']:
            email = member['email'].lower()
            username = email.split('@')[0]
            role = 'faculty' if member['role'] == 'faculty' else 'student'
            
            # Parse full name into first and last name
            full_name = member.get('name', '').strip()
            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            user, created = AdminUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'role': role,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            # Update only if user was just created or has no name set
            if created:
                # Already set via defaults
                pass
            else:
                # Only update name if both first_name and last_name are empty
                if not user.first_name and not user.last_name and full_name:
                    parts = full_name.split(maxsplit=1)
                    user.first_name = parts[0] if len(parts) > 0 else ''
                    user.last_name = parts[1] if len(parts) > 1 else ''
                # Update email only if missing
                if not user.email:
                    user.email = email
            
            # Generate random password for new users
            random_password = secrets.token_urlsafe(10)
            user.set_password(random_password)
            user.save()

            created_users.append({'user': user, 'password': random_password, 'member': member})
            if member['role'] == 'faculty':
                faculty_user = user

        # Create club
        # Extract faculty mentor name from members
        faculty_mentor_name = ''
        for member in data['members']:
            if member['role'] == 'faculty':
                faculty_mentor_name = member.get('name', '')
                break
        
        club = Club.objects.create(
            name=data['name'],
            club_number=data['club_number'],
            faculty_mentor=faculty_user,
            faculty_mentor_name=faculty_mentor_name
        )

        # Create memberships
        for entry in created_users:
            ClubMember.objects.create(
                club=club,
                user=entry['user'],
                role=entry['member']['role'],
                department=entry['member'].get('department', ''),
                academic_year=entry['member'].get('academic_year', ''),
            )

        # Generate PDF declaration and upload to S3
        try:
            from io import BytesIO
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            p.setFont("Helvetica-Bold", 16)
            p.drawString(72, 800, "Declaration of Inclusion")
            p.setFont("Helvetica", 12)
            p.drawString(72, 770, f"Club: {club.name} ({club.club_number})")
            p.drawString(72, 750, f"Issued On: {club.created_at.strftime('%Y-%m-%d')}")
            p.drawString(72, 730, "Members:")
            y = 710
            for m in club.members.all():
                text = f"- {m.user.username} ({m.user.email}) - {m.role.title()}"
                p.drawString(90, y, text)
                y -= 18
                if y < 100:
                    p.showPage()
                    y = 800
            p.showPage()
            p.save()
            buffer.seek(0)

            # Upload to S3
            bucket = settings.AWS_STORAGE_BUCKET_NAME
            region = settings.AWS_S3_REGION_NAME
            access_key = settings.AWS_ACCESS_KEY_ID
            secret_key = settings.AWS_SECRET_ACCESS_KEY
            s3_client = boto3.client('s3', region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
            s3_key = f"clubs/{club.club_number}/declaration_{club.club_number}.pdf"
            s3_client.put_object(Bucket=bucket, Key=s3_key, Body=buffer.getvalue(), ContentType='application/pdf')
            declaration_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
            club.declaration_url = declaration_url
            club.save()
        except Exception as pdf_exc:
            # Not critical to block creation
            print(f"PDF generation/upload failed: {pdf_exc}")

        # Generate presigned URL for declaration before sending emails
        declaration_url_to_send = club.declaration_url
        if club.declaration_url:
            prefix = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/"
            if club.declaration_url.startswith(prefix):
                key = club.declaration_url[len(prefix):]
                try:
                    s3_client = boto3.client(
                        's3',
                        region_name=settings.AWS_S3_REGION_NAME,
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                    )
                    declaration_url_to_send = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key},
                        ExpiresIn=604800  # 7 days
                    )
                    print(f"Generated presigned URL for declaration: {declaration_url_to_send[:80]}...")
                except Exception as presign_exc:
                    print(f"Presigned URL generation failed: {presign_exc}")

        # Send emails with credentials and declaration link
        from django.core.mail import send_mail
        for entry in created_users:
            member = entry['member']
            user = entry['user']
            pwd = entry['password']
            role_label = member['role'].replace('_', ' ').title()
            member_name = member.get('name', user.username)
            body = (
                f"Hello {member_name},\n\n"
                f"You have been added to the club '{club.name}' as {role_label}.\n"
                f"Login credentials:\nUsername: {user.username}\nPassword: {pwd}\n\n"
                f"Declaration link: {declaration_url_to_send or 'TBD'}\n\n"
                "Regards, CAMPUSPHERE"
            )
            try:
                send_mail(
                    subject=f"{club.name} Club Membership",
                    message=body,
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'no-reply@campusphere.local',
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                print(f"Email sent successfully to {user.email}")
            except Exception as mail_exc:
                print(f"Email sending failed for {user.email}: {mail_exc}")

        return Response({
            'message': 'Club created successfully',
            'club_id': club.id,
            'declaration_url': declaration_url_to_send
        }, status=status.HTTP_201_CREATED)

    except Exception as exc:
        import traceback
        return Response({'error': 'Failed to create club', 'details': str(exc), 'traceback': traceback.format_exc() if settings.DEBUG else None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def membership_requests_view(request):
    """Get all pending membership requests across all clubs."""
    try:
        # Get pending club members
        pending_members = ClubMember.objects.filter(status='pending').select_related('club', 'user')
        
        serializer = ClubMemberDetailSerializer(pending_members, many=True)
        return Response({
            'requests': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as exc:
        return Response({'error': 'Failed to fetch membership requests', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_role_view(request, member_id):
    """Approve a pending role (Treasurer, Secretary, etc.)."""
    try:
        member = ClubMember.objects.select_related('club', 'user').get(id=member_id)
        
        if member.status == 'approved':
            return Response({'error': 'Role already approved'}, status=status.HTTP_400_BAD_REQUEST)
        
        if member.status == 'revoked':
            return Response({'error': 'Role has been revoked'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update member status
        member.status = 'approved'
        member.approved_at = timezone.now()
        member.approved_by = request.user
        member.save()
        
        # Create history record
        RoleHistory.objects.create(
            club_member=member,
            action='approved',
            performed_by=request.user,
            remarks=request.data.get('remarks', '')
        )
        
        serializer = ClubMemberDetailSerializer(member)
        return Response({
            'message': 'Role approved successfully',
            'member': serializer.data
        }, status=status.HTTP_200_OK)
    
    except ClubMember.DoesNotExist:
        return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response({'error': 'Failed to approve role', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_access_view(request, member_id):
    """Revoke access for a club member."""
    try:
        member = ClubMember.objects.select_related('club', 'user').get(id=member_id)
        
        if member.status == 'revoked':
            return Response({'error': 'Access already revoked'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update member status
        old_status = member.status
        member.status = 'revoked'
        member.revoked_at = timezone.now()
        member.revoked_by = request.user
        member.save()
        
        # Create history record
        RoleHistory.objects.create(
            club_member=member,
            action='revoked',
            performed_by=request.user,
            remarks=request.data.get('remarks', '')
        )
        
        serializer = ClubMemberDetailSerializer(member)
        return Response({
            'message': 'Access revoked successfully',
            'member': serializer.data
        }, status=status.HTTP_200_OK)
    
    except ClubMember.DoesNotExist:
        return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response({'error': 'Failed to revoke access', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_history_view(request):
    """Get role history audit trail."""
    try:
        club_id = request.query_params.get('club_id')
        member_id = request.query_params.get('member_id')
        
        history = RoleHistory.objects.select_related('club_member__club', 'club_member__user', 'performed_by')
        
        if club_id:
            history = history.filter(club_member__club_id=club_id)
        
        if member_id:
            history = history.filter(club_member_id=member_id)
        
        serializer = RoleHistorySerializer(history, many=True)
        return Response({
            'history': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as exc:
        return Response({'error': 'Failed to fetch role history', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def club_members_view(request, club_id):
    """Get all members of a specific club."""
    try:
        members = ClubMember.objects.filter(club_id=club_id).select_related('club', 'user', 'approved_by', 'revoked_by')
        
        serializer = ClubMemberDetailSerializer(members, many=True)
        return Response({
            'members': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as exc:
        return Response({'error': 'Failed to fetch club members', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== APPROVAL MANAGEMENT ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def approvals_view(request):
    """
    GET: List all approval requests (with optional filters)
    POST: Create a new approval request
    """
    if request.method == 'GET':
        try:
            # Get filter parameters
            request_type = request.query_params.get('type')
            status_filter = request.query_params.get('status', 'pending')
            club_id = request.query_params.get('club_id')
            
            approvals = ApprovalRequest.objects.select_related(
                'club', 'requested_by', 'approved_by', 'rejected_by'
            ).prefetch_related('history__performed_by')
            
            # Apply filters
            if request_type and request_type != 'all':
                approvals = approvals.filter(request_type=request_type)
            
            if status_filter and status_filter != 'all':
                approvals = approvals.filter(status=status_filter)
            
            if club_id:
                approvals = approvals.filter(club_id=club_id)
            
            serializer = ApprovalRequestSerializer(approvals, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as exc:
            return Response({'error': 'Failed to fetch approvals', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'POST':
        try:
            serializer = ApprovalRequestCreateSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the approval request
            approval = serializer.save(requested_by=request.user)
            
            # Create history entry
            ApprovalHistory.objects.create(
                approval_request=approval,
                action='created',
                performed_by=request.user,
                comment='Approval request created'
            )
            
            response_serializer = ApprovalRequestSerializer(approval)
            return Response({
                'message': 'Approval request created successfully',
                'approval': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as exc:
            return Response({'error': 'Failed to create approval request', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def approval_detail_view(request, approval_id):
    """Get detailed information about a specific approval request."""
    try:
        approval = ApprovalRequest.objects.select_related(
            'club', 'requested_by', 'approved_by', 'rejected_by'
        ).prefetch_related('history__performed_by').get(id=approval_id)
        
        serializer = ApprovalRequestSerializer(approval)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ApprovalRequest.DoesNotExist:
        return Response({'error': 'Approval request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response({'error': 'Failed to fetch approval details', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_request_view(request, approval_id):
    """Approve an approval request."""
    try:
        from django.utils import timezone
        
        approval = ApprovalRequest.objects.get(id=approval_id)
        
        if approval.status == 'approved':
            return Response({'error': 'Request already approved'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update approval
        approval.status = 'approved'
        approval.approved_by = request.user
        approval.reviewed_at = timezone.now()
        
        # Add admin notes if provided
        if 'admin_notes' in request.data:
            approval.admin_notes = request.data['admin_notes']
        
        approval.save()
        
        # Create history entry
        ApprovalHistory.objects.create(
            approval_request=approval,
            action='approved',
            performed_by=request.user,
            comment=request.data.get('comment', 'Request approved')
        )
        
        serializer = ApprovalRequestSerializer(approval)
        return Response({
            'message': 'Request approved successfully',
            'approval': serializer.data
        }, status=status.HTTP_200_OK)
    
    except ApprovalRequest.DoesNotExist:
        return Response({'error': 'Approval request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response({'error': 'Failed to approve request', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_request_view(request, approval_id):
    """Reject an approval request."""
    try:
        from django.utils import timezone
        
        approval = ApprovalRequest.objects.get(id=approval_id)
        
        if approval.status == 'rejected':
            return Response({'error': 'Request already rejected'}, status=status.HTTP_400_BAD_REQUEST)
        
        if approval.status == 'approved':
            return Response({'error': 'Cannot reject an approved request'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Require rejection reason
        rejection_reason = request.data.get('rejection_reason')
        if not rejection_reason:
            return Response({'error': 'Rejection reason is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update approval
        approval.status = 'rejected'
        approval.rejected_by = request.user
        approval.reviewed_at = timezone.now()
        approval.rejection_reason = rejection_reason
        
        # Add admin notes if provided
        if 'admin_notes' in request.data:
            approval.admin_notes = request.data['admin_notes']
        
        approval.save()
        
        # Create history entry
        ApprovalHistory.objects.create(
            approval_request=approval,
            action='rejected',
            performed_by=request.user,
            comment=f'Request rejected: {rejection_reason}'
        )
        
        serializer = ApprovalRequestSerializer(approval)
        return Response({
            'message': 'Request rejected',
            'approval': serializer.data
        }, status=status.HTTP_200_OK)
    
    except ApprovalRequest.DoesNotExist:
        return Response({'error': 'Approval request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response({'error': 'Failed to reject request', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_under_review_view(request, approval_id):
    """Mark an approval request as under review."""
    try:
        approval = ApprovalRequest.objects.get(id=approval_id)
        
        if approval.status != 'pending':
            return Response({'error': 'Can only mark pending requests as under review'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status
        approval.status = 'under_review'
        approval.save()
        
        # Create history entry
        ApprovalHistory.objects.create(
            approval_request=approval,
            action='under_review',
            performed_by=request.user,
            comment='Request is now under review'
        )
        
        serializer = ApprovalRequestSerializer(approval)
        return Response({
            'message': 'Request marked as under review',
            'approval': serializer.data
        }, status=status.HTTP_200_OK)
    
    except ApprovalRequest.DoesNotExist:
        return Response({'error': 'Approval request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response({'error': 'Failed to update status', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def approval_history_view(request, approval_id):
    """Get the complete history of an approval request."""
    try:
        history = ApprovalHistory.objects.filter(
            approval_request_id=approval_id
        ).select_related('performed_by').order_by('-timestamp')
        
        serializer = ApprovalHistorySerializer(history, many=True)
        return Response({
            'history': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as exc:
        return Response({'error': 'Failed to fetch approval history', 'details': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
