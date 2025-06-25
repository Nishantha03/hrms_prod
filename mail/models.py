from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.EmailField(max_length=254)
    receiver = models.EmailField(max_length=254)
    subject = models.CharField(max_length=255, blank=True, null=True) 
    content = models.TextField()
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)  
    user_name = models.CharField(max_length=20,blank=True, null=True) 
    user_image = models.ImageField(upload_to='mail/',null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"
