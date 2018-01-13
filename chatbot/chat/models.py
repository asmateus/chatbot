"""
    Chat models are reduced to a Profile and a Message.
    The profile has a OneToOne relationship with the User
    model provided by Django authentication system.
"""

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # Some profile information
    description = models.TextField(max_length=600, blank=True)
    location = models.CharField(max_length=100, blank=True)


class Message(models.Model):
    origin = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='origin')
    target = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='target')
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


# Receiving methods for Profile and User synchronization

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
