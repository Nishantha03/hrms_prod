from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .utils import send_approval_email_to_user  # Import the helper function

@receiver(post_save, sender=User)
def send_approval_email(sender, instance, created, **kwargs):
    """Signal handler for account approval."""
    if not created:  # Ignore newly created users
        previous_instance = sender.objects.get(pk=instance.pk)
        if not previous_instance.is_active and instance.is_active:  # Check if the user is being approved
            send_approval_email_to_user(instance.email, instance.username)
