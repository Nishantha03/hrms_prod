from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.http import JsonResponse


def send_approval_email_to_user(email, username):
    """Helper function to send the approval email."""
    subject = "Your Account Approval Confirmation"
    message = (
        f"Dear {username},\n\n"
        f"We are pleased to inform you that your account has been successfully approved.\n\n"
        f"You can now log in to access your HRMS account and our services.\n\n"
        f"If you have any questions or need assistance, feel free to contact us.\n\n"
        f"Best regards,\n"
        f"The HR Team"
    )
    from_email = 'hr_user@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=User)
def send_approval_email(sender, instance, created, **kwargs):
    """Signal handler to send email when the user is approved."""
    if not created:  # Only proceed if the user already exists
        # Fetch the previous state of the user
        previous_instance = sender.objects.get(pk=instance.pk)
        if not previous_instance.is_active and instance.is_active:
            send_approval_email_to_user(instance.email, instance.username)


# In your approve_user view
def approve_user(request, user_id):
    """View function to approve a user."""
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()  # Triggers the signal
    return JsonResponse({"message": "User approved and email sent."})
