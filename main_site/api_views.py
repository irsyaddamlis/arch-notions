from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
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

from .models import (Article, Category, IndicatorSnapshot, TrendSnapshot,
                     UserProfile)

# ============================================================
# CURRENT USER
# ============================================================

@api_view(['GET'])
@authentication_classes([
    SessionAuthentication,
    TokenAuthentication,
])
@permission_classes([IsAuthenticated])
def me(request):

    profile = get_object_or_404(
        UserProfile,
        user=request.user
    )

    return Response({

        'username': request.user.username,

        'is_superuser': (
            request.user.is_superuser
        ),

        'is_approved': (
            profile.is_approved
        ),

        'can_view_all': (
            profile.can_view_all
        ),

        'can_download_all': (
            profile.can_download_all
        ),

    })


# ============================================================
# ARTICLES
# ============================================================

@api_view(['GET'])
@authentication_classes([
    SessionAuthentication,
    TokenAuthentication,
])
@permission_classes([IsAuthenticated])
def articles(request):

    profile = None

    # --------------------------------------------------------
    # Check approval
    # --------------------------------------------------------

    if not request.user.is_superuser:

        profile = get_object_or_404(
            UserProfile,
            user=request.user
        )

        if not profile.is_approved:

            return Response(
                {
                    'detail': (
                        'Your account is waiting approval.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----------------------------------------------------
        # User can see all articles
        # ----------------------------------------------------

        if profile.can_view_all:

            qs = Article.objects.all()

        # ----------------------------------------------------
        # User can only see allowed articles
        # ----------------------------------------------------

        else:

            qs = Article.objects.filter(
                Q(
                    allowed_view_users=request.user
                )
            ).distinct()

    else:

        qs = Article.objects.all()

    # Optimize ForeignKey query
    qs = qs.select_related('category')

    items = []

    for article in qs:

        # ----------------------------------------------------
        # Category
        # ----------------------------------------------------

        if article.category:

            category_name = (
                article.category.name
            )

        else:

            category_name = ''

        # ----------------------------------------------------
        # Download permission
        # ----------------------------------------------------

        if request.user.is_superuser:

            is_downloadable = True

        else:

            is_downloadable = (

                article.is_downloadable

                or profile.can_download_all #type: ignore

            )

        # ----------------------------------------------------
        # Article payload
        # ----------------------------------------------------

        items.append({

            'id': article.id, # type: ignore

            'date': (
                article.date.isoformat()
            ),

            'title': article.title,

            'category': category_name,

            'category_display': category_name,

            'creator': article.creator,

            'file_type': article.file_type,

            'file_url': request.build_absolute_uri(

                reverse(
                    'article_file',
                    args=[article.id] # type: ignore
                )

            ),

            'is_downloadable': (
                is_downloadable
            ),

        })

    # ========================================================
    # CATEGORY LIST
    # ========================================================
    CHOICES_MAP = dict(Article.CATEGORY_CHOICES)
    db_categories =[]
    for category in Category.objects.all():
        raw_val = category.name
        # 1. First choice: Use the exact human label from CATEGORY_CHOICES if mapped
        # 2. Fallback: Clean up any ad-hoc raw slug if not found in CATEGORY_CHOICES
        label = CHOICES_MAP.get(
        raw_val,
        raw_val.replace('_', ' ').replace('-', ' ').title()
        )
        db_categories.append({
            'value': raw_val,
            'label': label,
        })
    # Fallback to old choices
    if not db_categories:
        db_categories = [
            {
                'value': value,
                'label': label,
            }
            for value, label
            in Article.CATEGORY_CHOICES
        ]

    return Response({

        'results': items,

        'categories': db_categories,

    })


# ============================================================
# MANAGE USERS
# ============================================================

@api_view(['GET'])
@authentication_classes([
    SessionAuthentication,
    TokenAuthentication,
])
@permission_classes([IsAuthenticated])
def manage_users(request):

    if not request.user.is_superuser:

        return Response(
            {
                'detail': 'Forbidden'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    users = (

        User.objects

        .filter(
            is_superuser=False
        )

        .select_related(
            'userprofile'
        )

    )

    payload = []

    for user in users:

        payload.append({

            'id': user.id, # type: ignore

            'username': user.username,

            'email': user.email,

            'is_approved': (
                user.userprofile.is_approved # type: ignore
            ),

            'can_view_all': (
                user.userprofile.can_view_all # type: ignore
            ),

            'can_download_all': (
                user.userprofile.can_download_all # type: ignore
            ),

        })

    return Response({

        'results': payload

    })


# ============================================================
# MANAGE USER ACTIONS
# ============================================================

@api_view(['POST'])
@csrf_exempt
@authentication_classes([
    SessionAuthentication,
    TokenAuthentication,
])
@permission_classes([IsAuthenticated])
def manage_users_action(request):

    if not request.user.is_superuser:

        return Response(
            {
                'detail': 'Forbidden'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    user_id = request.data.get(
        'user_id'
    )

    action = request.data.get(
        'action'
    )

    try:

        target_user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        return Response(
            {
                'detail': 'User not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if target_user.is_superuser:

        return Response(
            {
                'detail': (
                    'Cannot modify superuser'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    profile, _ = (

        UserProfile.objects

        .get_or_create(
            user=target_user
        )

    )

    # --------------------------------------------------------
    # Toggle approval
    # --------------------------------------------------------

    if action == 'toggle_approval':

        profile.is_approved = (

            not profile.is_approved

        )

        profile.can_view_all = (

            profile.is_approved

        )

        if not profile.is_approved:

            profile.can_download_all = False

        profile.save()

        return Response({
            'ok': True
        })

    # --------------------------------------------------------
    # Toggle download permission
    # --------------------------------------------------------

    if action == 'toggle_download':

        if not profile.is_approved:

            return Response(
                {
                    'detail': (
                        'User must be approved '
                        'before granting download access.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        profile.can_download_all = (

            not profile.can_download_all

        )

        profile.save()

        return Response({
            'ok': True
        })

    return Response(
        {
            'detail': 'Invalid action'
        },
        status=status.HTTP_400_BAD_REQUEST
    )


# ============================================================
# HELPER: GET CATEGORY
# ============================================================

def get_category_from_request(
    category_code
):

    """
    Convert the category value sent by the frontend
    into a Category model instance.

    Example:

        "whitepaper"

    becomes:

        Category.objects.get(
            name="whitepaper"
        )
    """

    if not category_code:

        return None

    try:

        return Category.objects.get(
            name=category_code
        )

    except Category.DoesNotExist:

        return None


# ============================================================
# UPLOAD ARTICLE
# ============================================================

@api_view(['POST'])
@csrf_exempt
@authentication_classes([
    SessionAuthentication,
    TokenAuthentication,
])
@permission_classes([IsAuthenticated])
def upload_article(request):

    if not request.user.is_superuser:

        return Response(
            {
                'detail': 'Forbidden'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    title = request.data.get(
        'title'
    )

    date = request.data.get(
        'date'
    )

    file_type = request.data.get(
        'file_type'
    )

    if not title or not date:

        return Response(
            {
                'detail': (
                    'title and date are required'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # Download permission
    # --------------------------------------------------------

    raw_downloadable = request.data.get(
        'is_downloadable'
    )

    is_downloadable = (

        raw_downloadable

        in [
            'true',
            'True',
            True,
            1,
            '1',
        ]

    )

    # --------------------------------------------------------
    # Google Drive file ID
    # --------------------------------------------------------

    drive_file_id = request.data.get(
        'drive_file_id'
    )

    if not drive_file_id:

        return Response(
            {
                'detail': (
                    'drive_file_id is required'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category_code = (

        request.data.get(
            'category'
        )

        or Article.CATEGORY_WHITEPAPER

    )

    category = get_category_from_request(
        category_code
    )

    if category is None:

        return Response(
            {
                'detail': (
                    f"Category '{category_code}' "
                    'does not exist.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # Other fields
    # --------------------------------------------------------

    creator = request.data.get(
        'creator',
        ''
    )

    # --------------------------------------------------------
    # Create article
    # --------------------------------------------------------

    Article.objects.create(

        date=date,

        title=title,

        category=category,

        creator=creator,

        file_type=file_type,

        drive_file_id=drive_file_id,

        is_downloadable=is_downloadable,

    )

    return Response({

        'ok': True

    })


# ============================================================
# EDIT ARTICLE
# ============================================================

@api_view(['POST'])
@csrf_exempt
@authentication_classes([
    SessionAuthentication,
    TokenAuthentication,
])
@permission_classes([IsAuthenticated])
def edit_article(request):

    # --------------------------------------------------------
    # Only admin can edit articles
    # --------------------------------------------------------

    if not request.user.is_superuser:

        return Response(
            {
                'detail': 'Forbidden'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # --------------------------------------------------------
    # Get article ID
    # --------------------------------------------------------

    article_id = request.data.get(
        'article_id'
    )

    try:

        article = Article.objects.get(
            id=article_id
        )

    except Article.DoesNotExist:

        return Response(
            {
                'detail': 'Article not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    title = request.data.get(
        'title'
    )

    date = request.data.get(
        'date'
    )

    if not title or not date:

        return Response(
            {
                'detail': (
                    'title and date are required'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ========================================================
    # CATEGORY FIX
    # ========================================================

    category_code = request.data.get(
        'category'
    )

    # If frontend sends a new category
    if category_code:

        category = get_category_from_request(
            category_code
        )

        if category is None:

            return Response(
                {
                    'detail': (
                        f"Category '{category_code}' "
                        'does not exist.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # If category is not sent,
    # keep the current Category object
    else:

        category = article.category

    # ========================================================
    # UPDATE ARTICLE
    # ========================================================

    article.title = title

    article.date = date

    article.category = category

    article.creator = request.data.get(

        'creator',

        article.creator

    )

    # --------------------------------------------------------
    # is_downloadable
    # --------------------------------------------------------

    if 'is_downloadable' in request.data:

        raw_downloadable = request.data.get(

            'is_downloadable'

        )

        article.is_downloadable = (

            raw_downloadable

            in [
                'true',
                'True',
                True,
                1,
                '1',
            ]

        )

    article.save()

    return Response({

        'ok': True,

        'message': (
            'Article updated successfully'
        )

    })


# ============================================================
# DELETE ARTICLE
# ============================================================

@api_view(['POST'])
@csrf_exempt
@authentication_classes([
    SessionAuthentication,
    TokenAuthentication,
])
@permission_classes([IsAuthenticated])
def delete_article(request):

    if not request.user.is_superuser:

        return Response(
            {
                'detail': 'Forbidden'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    article_id = request.data.get(
        'article_id'
    )

    try:

        article = Article.objects.get(
            id=article_id
        )

    except Article.DoesNotExist:

        return Response(
            {
                'detail': 'Article not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # --------------------------------------------------------
    # Delete local file if present
    # --------------------------------------------------------

    if article.file:

        article.file.delete(
            save=False
        )

    # --------------------------------------------------------
    # Delete database record
    # --------------------------------------------------------

    article.delete()

    return Response({

        'ok': True

    })


# ============================================================
# PASSWORD RESET REQUEST
# ============================================================

@api_view(['POST'])
def password_reset_request(request):

    email = request.data.get(
        'email'
    )

    # Do not reveal whether email exists
    try:

        user_model = get_user_model()

        user = user_model.objects.get(
            email=email
        )

    except Exception:

        return Response({

            'ok': True

        })

    # --------------------------------------------------------
    # Generate reset token
    # --------------------------------------------------------

    uidb64 = urlsafe_base64_encode(

        force_bytes(
            user.pk
        )

    )

    token = default_token_generator.make_token(
        user
    )

    # --------------------------------------------------------
    # Build reset URL
    # --------------------------------------------------------

    domain = request.get_host()

    scheme = (

        'https'

        if request.is_secure()

        else 'http'

    )

    reset_url = (

        f'{scheme}://{domain}'

        f'/password-reset-confirm/'

        f'{uidb64}/{token}/'

    )

    subject = 'Password reset'

    message = (

        'Someone requested a password reset '
        'for your account.\n\n'

        f'Click this link to reset your password: '

        f'{reset_url}\n\n'

        'If you did not request this, '
        'ignore this email.'

    )

    send_mail(

        subject,

        message,

        settings.DEFAULT_FROM_EMAIL,

        [user.email],

        fail_silently=False,

    )

    return Response({

        'ok': True

    })


# ============================================================
# PASSWORD RESET CONFIRM
# ============================================================

@api_view(['POST'])
def password_reset_confirm(request):

    uidb64 = request.data.get(
        'uidb64'
    )

    token = request.data.get(
        'token'
    )

    new_password1 = request.data.get(
        'new_password1'
    )

    new_password2 = request.data.get(
        'new_password2'
    )

    try:

        user_model = get_user_model()

        uid = (

            urlsafe_base64_decode(
                uidb64
            )

            .decode()

        )

        user = (

            user_model

            ._default_manager

            .get(
                pk=uid
            )

        )

    except Exception:

        return Response(
            {
                'detail': 'Invalid link'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # Validate token
    # --------------------------------------------------------

    if not default_token_generator.check_token(
        user,
        token
    ):

        return Response(
            {
                'detail': (
                    'Invalid or expired token'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    form = SetPasswordForm(

        user,

        {

            'new_password1': new_password1,

            'new_password2': new_password2,

        }

    )

    if not form.is_valid():

        return Response(
            {
                'detail': (
                    'Invalid password reset'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    form.save()

    return Response({

        'ok': True

    })


# ============================================================
# INDICATORS
# ============================================================

class IndicatorsView(APIView):

    """
    GET /api/indicators/

    Returns:

    {
        "id_debt": "...",
        "usd_idr": "...",
        ...
    }
    """

    def get(
        self,
        request
    ):

        rows = IndicatorSnapshot.objects.all()

        data = {

            row.key: row.value

            for row in rows

        }

        return Response(
            data
        )


# ============================================================
# TREND
# ============================================================

class TrendView(APIView):

    """
    GET /api/trend/

    Returns:

    [
        {
            "date": "...",
            "ihsg": ...,
            "exchange": ...
        }
    ]
    """

    def get(
        self,
        request
    ):

        snapshot = (

            TrendSnapshot.objects

            .first()

        )

        data = (

            snapshot.data

            if snapshot

            else []

        )

        return Response(
            data
        )