from django.conf import settings
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, IndicatorSnapshot, TrendSnapshot, UserProfile


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return Response(
        {
            'username': request.user.username,
            'is_superuser': request.user.is_superuser,
            'is_approved': profile.is_approved,
            'can_view_all': profile.can_view_all,
            'can_download_all': profile.can_download_all,
        }
    )


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def articles(request):
    # Enforce approval server-side
    if not request.user.is_superuser:
        profile = get_object_or_404(UserProfile, user=request.user)
        if not profile.is_approved:
            return Response(
                {'detail': 'Your account is waiting approval.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Filter based on specific user access or global view permission
        if not profile.can_view_all:
            qs = Article.objects.filter(
                Q(allowed_view_users=request.user)
            ).distinct()
        else:
            qs = Article.objects.all()
    else:
        qs = Article.objects.all()

    items = []
    for a in qs:
        items.append(
            {
                'id': a.id, # type: ignore
                'title': a.title,
                'date': a.date.isoformat(),
                'file_type': a.file_type,
                'file_url': request.build_absolute_uri(a.file.url),
                'is_downloadable': a.is_downloadable or (not request.user.is_superuser and profile.can_download_all), # type: ignore
            }
        )

    return Response({'results': items})


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def manage_users(request):
    if not request.user.is_superuser:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.filter(is_superuser=False).select_related('userprofile')
    payload = []
    for u in users:
        payload.append(
            {
                'id': u.id, # type: ignore
                'username': u.username,
                'email': u.email,
                'is_approved': u.userprofile.is_approved, # type: ignore
                'can_view_all': u.userprofile.can_view_all, # type: ignore
                'can_download_all': u.userprofile.can_download_all, # type: ignore
            }
        )
    return Response({'results': payload})


@api_view(['POST'])
@csrf_exempt
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def manage_users_action(request):
    if not request.user.is_superuser:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    action = request.data.get('action')

    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if target_user.is_superuser:
        return Response({'detail': 'Cannot modify superuser'}, status=status.HTTP_400_BAD_REQUEST)

    profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if action == 'toggle_approval':
        profile.is_approved = not profile.is_approved
        profile.can_view_all = profile.is_approved
        if not profile.is_approved:
            profile.can_download_all = False  # revoke download if unapproved
        profile.save()
        return Response({'ok': True})
    
    if action == 'toggle_download':
        if not profile.is_approved:
            return Response(
                {'detail': 'User must be approved before granting download access.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        profile.can_download_all = not profile.can_download_all
        profile.save()
        return Response({'ok': True})

    return Response({'detail': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_article(request):
    if not request.user.is_superuser:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    title = request.data.get('title')
    date = request.data.get('date')
    file_type = request.data.get('file_type')
    if not title or not date:
        return Response({'detail': 'title and date are required'}, status=status.HTTP_400_BAD_REQUEST)

    is_downloadable = (
        'is_downloadable' in request.data
        or request.data.get('is_downloadable') in ['true', 'True', True, 1, '1']
    )

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({'detail': 'file is required'}, status=status.HTTP_400_BAD_REQUEST)

    Article.objects.create(
        title=title,
        date=date,
        file_type=file_type,
        file=uploaded_file,
        is_downloadable=is_downloadable,
    )
    return Response({'ok': True})


@api_view(['POST'])
def password_reset_request(request):
    email = request.data.get('email')

    # Always return success to avoid leaking user existence.
    # If the email exists, we send a reset link.
    try:
        user_model = get_user_model()
        user = user_model.objects.get(email=email)
    except Exception:
        return Response({'ok': True})

    # Create uidb64 + token (same mechanism Django uses)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Build reset URL (must match the route we redirected to Flet)
    domain = request.get_host()
    scheme = 'https' if request.is_secure() else 'http'
    reset_url = f"{scheme}://{domain}/password-reset-confirm/{uidb64}/{token}/"

    subject = 'Password reset'
    message = (
        'Someone requested a password reset for your account.\n\n'
        f'Click this link to reset your password: {reset_url}\n\n'
        'If you did not request this, ignore this email.'
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    return Response({'ok': True})


@api_view(['POST'])
def password_reset_confirm(request):
    uidb64 = request.data.get('uidb64')
    token = request.data.get('token')
    new_password1 = request.data.get('new_password1')
    new_password2 = request.data.get('new_password2')

    try:
        user_model = get_user_model()
        uid = urlsafe_base64_decode(uidb64).decode()
        user = user_model._default_manager.get(pk=uid)
    except Exception:
        return Response({'detail': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

    form = SetPasswordForm(
        user,
        {
            'new_password1': new_password1,
            'new_password2': new_password2,
        },
    )

    if not form.is_valid():
        return Response({'detail': 'Invalid password reset'}, status=status.HTTP_400_BAD_REQUEST)

    form.save()
    return Response({'ok': True})

# Add this function to api_views.py, alongside upload_article.
# Deletes both the DB record and the underlying file from storage.

@api_view(['POST'])
@csrf_exempt
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_article(request):
    if not request.user.is_superuser:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    article_id = request.data.get('article_id')

    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response({'detail': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

    # Remove the underlying file from storage, not just the DB row.
    if article.file:
        article.file.delete(save=False)
    article.delete()

    return Response({'ok': True})


class IndicatorsView(APIView):
    """
    GET /api/indicators/
    Returns a flat object: { "id_debt": "...", "usd_idr": "...", ... }
    """
 
    def get(self, request):
        rows = IndicatorSnapshot.objects.all()
        data = {row.key: row.value for row in rows}
        return Response(data)
 
 
class TrendView(APIView):
    """
    GET /api/trend/
    Returns the stored trend series as a plain array:
    [{ "date": "...", "ihsg": ..., "exchange": ... }, ...]
    """
 
    def get(self, request):
        snapshot = TrendSnapshot.objects.first()
        data = snapshot.data if snapshot else []
        return Response(data)