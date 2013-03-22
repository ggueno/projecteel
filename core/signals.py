from django.db.models.signals import post_save
from notifications import notify
from core.models import Follow

def has_follow(sender, instance, created, **kwargs):
    notify.send(instance.follower, recipient=instance.follower.user, verb='has followed you.')

post_save.connect(has_follow, sender=Follow)
