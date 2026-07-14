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