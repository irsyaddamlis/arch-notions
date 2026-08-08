from django.contrib import admin

from .models import Article, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'is_approved', 'can_view_all', 'can_download_all')
    list_filter = ('is_approved', 'can_view_all', 'can_download_all')
    search_fields = ('user__username', 'user__email')

    @admin.display(description='Email', ordering='user__email')
    def get_email(self, obj):
        return obj.user.email


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'file_type', 'category', 'creator_name')
    filter_horizontal = ('allowed_view_users', 'allowed_download_users')
    search_fields = ('title',)
    list_filter = ('date', 'file_type')