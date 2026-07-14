from django.contrib import admin

from .models import Article, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'user__email')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'file_type', 'is_downloadable')
    # This creates a much better UI for selecting multiple users
    filter_horizontal = ('allowed_view_users', 'allowed_download_users')
    search_fields = ('title',)
    list_filter = ('date', 'file_type')
