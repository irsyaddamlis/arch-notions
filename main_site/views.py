from datetime import date
from typing import Any

import gdc  # type: ignore
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

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
            "name": "AI-Driven Systems",
            "detail": "Implementing intelligent to digitize customer service operations and streamline internal knowledge management, enhancing both customer experience and operational efficiency."
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

def solution(request):
    return render(request, 'solution.html', _get_services_context())

# Protect articles page — redirect to login if not logged in.
# Approval/permission filtering now happens client-side via /api/articles/,
# which returns 403 for unapproved accounts and already filters the list
# server-side per user, so this view just needs to gate the page itself.
@login_required(login_url='/login')
def articles(request):
    return render(request, 'articles.html')


def _user_can_view_article(request, article) -> bool:
    """Same gate used by the `articles` list view, applied per-article."""
    if request.user.is_superuser:
        return True
    profile = getattr(request.user, 'userprofile', None)
    if not profile or not profile.is_approved:
        return False
    if profile.can_view_all:
        return True
    return article.allowed_view_users.filter(pk=request.user.pk).exists()


@login_required(login_url='/login')
def article_file(request, article_id):
    """Proxy endpoint: streams the file from Google Drive only after
    checking the same approval/permission rules used everywhere else.
    The Drive file itself can stay private — only the service account
    behind `gdc` needs access to it."""
    article = get_object_or_404(Article, id=article_id)

    if not _user_can_view_article(request, article):
        return HttpResponseForbidden("You do not have permission to view this article.")

    if not article.drive_file_id:
        raise Http404("This article has no linked file.")

    try:
        # Reuses gdc's cached/shared connector (same one read_pdf/read_word etc.
        # use internally) instead of re-authenticating on every request.
        connector = gdc._get_conn()

        meta = connector.drive_service.files().get(
            fileId=article.drive_file_id,
            fields="name,mimeType",
        ).execute()
        filename = meta.get("name") or f"article-{article.id}"
        mime_type = meta.get("mimeType") or "application/octet-stream"

        fh = connector.download_file_as_bytes(article.drive_file_id)
        file_bytes = fh.read()
    except Exception:
        import traceback
        traceback.print_exc()  # TEMP: prints the real error to the runserver console
        return HttpResponse("Could not retrieve the file from Google Drive.", status=502)

    response = HttpResponse(file_bytes, content_type=mime_type)
    disposition = "attachment" if request.GET.get("download") else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response

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
        drive_file_id = request.POST['drive_file_id']
        is_downloadable = 'is_downloadable' in request.POST

        Article.objects.create(
            title=title,
            date=date,
            file_type=file_type,
            drive_file_id=drive_file_id,
            is_downloadable=is_downloadable,
        )
        return redirect('articles')

    return render(request, 'upload_article.html')

@login_required(login_url='/login')
def features(request):
    return render(request, 'features.html')

def react_app(request):
    return render(request, 'base.html', {'is_react_app': True})

def indicators_view(request):
    return render(request, "indicators.html")