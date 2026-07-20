from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    can_view_all = models.BooleanField(default=False)
    can_download_all = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()


class Article(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='articles/')
    date = models.DateField()
    is_downloadable = models.BooleanField(default=False)
    file_type = models.CharField(max_length=10)
    allowed_view_users = models.ManyToManyField(
        User, blank=True, related_name='view_articles'
    )
    allowed_download_users = models.ManyToManyField(
        User, blank=True, related_name='download_articles'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']


class IndicatorSnapshot(models.Model):
    """
    One row per dashboard indicator (e.g. 'usd_idr', 'ihsg', 'bi_rate').
    Each refresh job overwrites the row for the keys it owns via
    update_or_create(), so the table never grows - it's always exactly
    one row per indicator, holding the latest known value.
    """
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"{self.key}: {self.value} (updated {self.updated_at:%Y-%m-%d %H:%M})"


class TrendSnapshot(models.Model):
    """
    Holds the latest 1-month IHSG / $-Exchange time series (the output of
    dashboard_model.trend()) as JSON, so the trend chart is served from
    the DB instead of hitting yfinance on every page load. Only ever one
    row - refreshed in place by refresh_market_hourly.
    """
    data = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TrendSnapshot ({len(self.data)} points, updated {self.updated_at:%Y-%m-%d %H:%M})"