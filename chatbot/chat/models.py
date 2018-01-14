"""
    Chat models are reduced to a Profile and a Message.
    The profile has a OneToOne relationship with the User
    model provided by Django authentication system.
"""

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver


class _MessageManager(models.Manager):
    DEFAULT_MESSAGE_LIMIT = 50

    def sanitize_raw_limit(self, raw_limit):
        limit = _MessageManager.DEFAULT_MESSAGE_LIMIT

        # Attempt retreival of raw limit
        try:
            limit = int(raw_limit)
        except Exception:
            pass
        else:
            if limit < -1:
                limit = 0

        return limit

    def of(self, username, limit=DEFAULT_MESSAGE_LIMIT):
        # Messages are from a user if the user is, either the
        # origin or the target.
        user = User.objects.get(username=username)
        query = models.Q(origin=user) | models.Q(target=user)

        # If user requested full output
        if limit == -1:
            return super().filter(query)
        return super().filter(query)[:limit]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # Some profile information
    description = models.TextField(max_length=600, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def update(self, data):
        self.user.first_name = data.get('first_name')
        self.user.last_name = data.get('last_name')

        self.description = data.get('description')
        self.location = data.get('location')


class Message(models.Model):
    origin = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='origin')
    target = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='target')
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Assign a special manager for this model
    objects = _MessageManager()

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
