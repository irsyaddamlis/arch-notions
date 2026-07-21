from django.contrib.auth import views as auth_views  # type: ignore
from django.http import HttpResponseRedirect  # type: ignore
from django.urls import include, path  # type: ignore

from . import views

#from .views import indicators_view

# Admin panel is now Reflex, not Flet. Reflex's frontend serves the pages
# themselves (backend_port 8560 is only for the websocket/state channel,
# never hit directly by the browser).
REFLEX_ADMIN_URL = "http://127.0.0.1:3550"
FLET_BASE_URL_RESET = "http://127.0.0.1:8551"

def redirect_to_reflex_admin(path_suffix: str):
    # Ensure absolute URL for production reverse-proxy setups too (dev uses localhost)
    path_suffix = path_suffix.strip("/")
    return HttpResponseRedirect(f"{REFLEX_ADMIN_URL}/{path_suffix}")

def redirect_to_flet_reset(path_suffix: str):
    # Ensure absolute URL for production reverse-proxy setups too (dev uses localhost)
    path_suffix = path_suffix.lstrip("/")
    return HttpResponseRedirect(f"{FLET_BASE_URL_RESET}/{path_suffix}")


urlpatterns = [
    path('', views.react_app, name='home'),
    path('profile/', views.profile, name='profile'),
    path('services/', views.services, name='services'),
    path('articles/', views.articles, name='articles'),
    path('features/', views.features, name='features'),

    # Include the API endpoints
    path('api/', include('main_site.api_urls')),

    # Reflex admin pages (redirects)
    path('upload-article/', lambda request: redirect_to_reflex_admin('upload-article/'), name='upload_article'),
    path('manage-users/', lambda request: redirect_to_reflex_admin('manage-users/'), name='manage_users'),

    # Auth stays in Django
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    path('app/', views.react_app, name='react_app'),

    # Password reset URLs must remain identical for email links.
    # UI is still provided by Flet (unchanged); actual reset handling goes through APIs.
    path('password-reset/', lambda request: redirect_to_flet_reset('password-reset/'), name='password_reset'),
    path('password-reset/done/', lambda request: redirect_to_flet_reset('password-reset/done/'), name='password_reset_done'),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        lambda request, uidb64, token: redirect_to_flet_reset(
            f'password-reset-confirm/{uidb64}/{token}/'
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        lambda request, uidb64, token: redirect_to_flet_reset(
            f'password-reset-confirm/{uidb64}/{token}/'
        ),
        name='password_reset_confirm_alias',
    ),
    path(
        'password-reset-confirm/<uidb64>/set-password/',
        lambda request, uidb64: redirect_to_flet_reset(
            f'password-reset-confirm/{uidb64}/-/'
        ),
        name='password_reset_confirm_set',
    ),
    path(
        'password-reset-complete/',
        lambda request: redirect_to_flet_reset('password-reset-complete/'),
        name='password_reset_complete',
    ),
    path("indicators/", views.indicators_view, name="indicators"),
]