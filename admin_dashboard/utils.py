from django.core.mail import send_mail

def send_approval_email_to_user(email, username):
    """Helper function to send an approval email."""
    subject = "Your Account Approval Confirmation"
    message = (
        f"Dear {username},\n\n"
        f"We are pleased to inform you that your account has been successfully approved.\n\n"
        f"You can now log in to access your HRMS account and our services.\n\n"
        f"If you have any questions or need assistance, feel free to contact us.\n\n"
        f"Best regards,\n"
        f"The HR Team"
    )
    from_email = 'your_email@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
