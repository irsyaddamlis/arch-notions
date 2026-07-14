from django.urls import path

from . import api_views

urlpatterns = [
    path('me/', api_views.me, name='api_me'),
    path('articles/', api_views.articles, name='api_articles'),

    path('upload-article/', api_views.upload_article, name='api_upload_article'),
    path('delete-article/', api_views.delete_article, name='api_delete_article'),
    path('manage-users/', api_views.manage_users, name='api_manage_users'),
    path('manage-users/action/', api_views.manage_users_action, name='api_manage_users_action'),

    path('password-reset-request/', api_views.password_reset_request, name='api_password_reset_request'),
    path('password-reset-confirm/', api_views.password_reset_confirm, name='api_password_reset_confirm'),
]