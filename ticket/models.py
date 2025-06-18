from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime

PRIORITY_TIMEFRAMES = {
    'High': timedelta(minutes=2),
    'Medium': timedelta(days=1),
    'Low': timedelta(days=3),
}

class Category(models.Model):
    name = models.CharField(max_length=255) 
    parent_name = models.CharField(max_length=255, null=True, blank=True)  
    assigned_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assign_user'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"



class Ticket(models.Model):
  
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    ticket_number = models.AutoField(primary_key=True) 
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    subcategory = models.CharField(max_length=255)  
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    description = models.TextField()
    username = models.CharField(max_length=255, null=True, blank=True)
    assigned_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    escalation = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    attachment = models.FileField(upload_to='ticket_attachments/', null=True, blank=True)
    attachment = models.FileField(upload_to='ticket_attachments/', null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_escalation_deadline(self):
        """Set escalation deadline based on priority"""
        if self.priority in PRIORITY_TIMEFRAMES:
            self.escalation = datetime.now() + PRIORITY_TIMEFRAMES[self.priority]
        else:
            self.escalation = None

    def save(self, *args, **kwargs):
        if not self.escalation:
            self.set_escalation_deadline()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.category}"
