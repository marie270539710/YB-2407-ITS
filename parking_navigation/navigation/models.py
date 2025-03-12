from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=20, blank=True)
    selected_slot = models.CharField(max_length=5, blank=True)
    selected_area = models.CharField(max_length=50, blank=True)
    arrival_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()