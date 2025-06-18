from django.db import models
from employees.models import Employee
from django.utils.timezone import now

class Attendance(models.Model):
    date = models.DateField(auto_now_add=True)
    day = models.CharField(max_length=10, null=True, blank=True) 
    clock_in = models.TimeField(null=True, blank=True) 
    clock_out = models.TimeField(null=True, blank=True)  
    status = models.CharField(
        max_length=10, 
        choices=[('Present', 'Present'), ('Absent', 'Absent')], 
        default='Missing'
    )
    user_id = models.IntegerField(null=True, blank=True)
    user_name = models.CharField(max_length=100, null=True, blank=True)
    working_hours = models.TimeField(null=True, blank=True)  
    late_arrival = models.TimeField(null=True, blank=True)  
    is_regularized = models.BooleanField(default=False)  
    submit_regularize = models.BooleanField(default=False) 
    regularization_reason = models.TextField(null=True, blank=True)  
    regularization_status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    
    approved_by = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_attendances"
    )
    approver =  models.CharField(max_length=10,null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.date:
            self.day = self.date.strftime('%A')  
        super().save(*args, **kwargs)

    def approve_regularization(self, approver):
        """Approve the regularization request."""
        self.regularization_status = "Approved"
        self.is_regularized = True
        self.approved_by = approver
        self.approved_at = now()
        self.save()

    def reject_regularization(self):
        """Reject the regularization request."""
        self.regularization_status = "Rejected"
        self.save()

    def __str__(self):
        return f"{self.date} - {self.approver} - {self.status} - {self.regularization_status}"
    
