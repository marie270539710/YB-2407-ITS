from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # email = models.CharField(max_length=20, blank=True)
    # contact_number = models.CharField(max_length=20, blank=True)
    plate_number = models.CharField(max_length=20, blank=True)
    selected_slot = models.CharField(max_length=5, blank=True)
    selected_area = models.CharField(max_length=50, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class ParkingLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.CharField(max_length=20)
    arrival_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    autoexit = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.username} - {self.slot} ({self.arrival_time.strftime('%Y-%m-%d %H:%M')})"

class AvailableSlot(models.Model):
    slots = models.TextField('Available Slots') 
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.slots}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()