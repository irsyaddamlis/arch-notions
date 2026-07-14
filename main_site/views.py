from datetime import date
from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render

from .models import Article, UserProfile


def _get_services_context() -> dict[str, Any]:
    core_services = [
        {
            "name": "Strategic Planning & Analytics",
            "detail": "Crafting comprehensive Business Plans and Business Cases"
        },
        {
            "name": "Business Projection & Valuation",
            "detail": "Developing Financial Models, Performance Dashboards, and Advanced Business Reporting"
        },
        {
            "name": "Project Management & Implementation",
            "detail": "Focusing on operational excellence and implementation strategy to ensure plans become reality"
        },
        {
            "name": "Local Market Analysis",
            "detail": "Deep-dive research and analysis to navigate the Indonesian market landscape"
        },
    ]
    other_services = [
        {
            "name": "Geospatial Analytics for Strategic Site Selection",
            "detail": "Utilizing advanced location intelligence to identify high-potential sites for new points of sale, ensuring data-driven expansion for your enterprise"
        },
        {
            "name": "AI-Driven Conversational Systems",
            "detail": "Implementing intelligent chatbots to digitize customer service operations and streamline internal knowledge management, enhancing both customer experience and operational efficiency."
        },
    ]
    return {
        'core_services': core_services,
        'other_services': other_services
    }

def profile(request):
    years = date.today().year - 2002
    context = {'years': years}
    context.update(_get_services_context())
    return render(request, 'profile.html', context)

def services(request):
    return render(request, 'services.html', _get_services_context())

# Protect articles page — redirect to login if not logged in
@login_required(login_url='/login')
def articles(request):
    # Check if the user is approved (Superusers bypass this check)
    if not request.user.is_superuser:
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_approved:
            messages.info(request, "Your Account is Waiting Approval")
            return render(request, 'articles.html', {'articles': []})

        # Filter articles based on permissions
        if not profile.can_view_all:
            articles = Article.objects.filter(
                Q(allowed_view_users=request.user)
            ).distinct()
        else:
            articles = Article.objects.all()
    else:
        articles = Article.objects.all()

    return render(request, 'articles.html', {'articles': articles})

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        messages.success(request, 'Account created, please log in')
        return redirect('login')

    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url or 'home')
        else:
            messages.error(request, 'Invalid username or password')

    next_url = request.GET.get('next', '')
    return render(request, 'login.html',  {'next': next_url})

def user_logout(request):
    logout(request)
    return redirect('home')

@user_passes_test(lambda u: u.is_superuser)
def upload_article(request):
    if request.method == 'POST':
        title = request.POST['title']
        date = request.POST['date']
        file_type = request.POST['file_type']
        file = request.FILES['file']
        is_downloadable = 'is_downloadable' in request.POST

        Article.objects.create(
            title=title,
            date=date,
            file_type=file_type,
            file=file,
            is_downloadable=is_downloadable
        )
        return redirect('articles')

    return render(request, 'upload_article.html')

@login_required(login_url='/login')
def features(request):
    return render(request, 'features.html')

def react_app(request):
    return render(request, 'base.html', {'is_react_app': True})

#@user_passes_test(lambda u: u.is_superuser)
#def manage_users(request):
#    if request.method == 'POST':
#        user_id = request.POST.get('user_id')
#        action = request.POST.get('action')
        
#        try:
#            target_user = User.objects.get(id=user_id)
#            if target_user.is_superuser:
#                messages.error(request, "Cannot modify superuser status.")
#            elif action == 'toggle_approval':
#                # Ensure profile exists, then toggle approval
#                profile, created = UserProfile.objects.get_or_create(user=target_user)
#                profile.is_approved = not profile.is_approved
#                profile.save()
#                messages.success(request, f"Access updated for {target_user.username}")
#            elif action == 'update_permissions':
                # Update global boolean flags on the profile
#                profile, _ = UserProfile.objects.get_or_create(user=target_user)
#                profile.can_view_all = 'can_view_all' in request.POST
#                profile.can_download_all = 'can_download_all' in request.POST
#                profile.save()
                
#                messages.success(request, f"Permissions updated for {target_user.username}")
#        except User.DoesNotExist:
#            messages.error(request, "User not found.")
        
#        return redirect('manage_users')

    # Fetch users with their profiles for display
#    users = User.objects.filter(is_superuser=False).select_related('userprofile')
#    return render(request, 'manage_users.html', {'users': users})