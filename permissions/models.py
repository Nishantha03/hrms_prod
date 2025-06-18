from django.db import models
from employees.models import Employee  
from datetime import timedelta

class Permission(models.Model):
    permission_id = models.AutoField(primary_key=True) 
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE, 
        related_name='permission'  
    )
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    leave_balance = models.FloatField(default=2.0)
    user_name = models.CharField(max_length=20, null=True)
    user_department = models.CharField(max_length=20, null=True)
    user_id = models.IntegerField()
    notes =  models.TextField(null=True)
    avail_permission = models.FloatField(default=0.0)
    session = models.CharField(max_length=20, null=True)
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
            return f"{self.employee.employee_first_name} {self.employee.employee_last_name}: {self.date} ({self.time_from} - {self.time_to})"

    def save(self, *args, **kwargs):
        if self.created_at:
            self.created_at = self.created_at.replace(microsecond=0)
        if self.updated_at:
            self.updated_at = self.updated_at.replace(microsecond=0)
        super().save(*args, **kwargs)
    @property
    def applied_hours(self):
        start = timedelta(hours=self.time_from.hour, minutes=self.time_from.minute)
        end = timedelta(hours=self.time_to.hour, minutes=self.time_to.minute)
        return (end - start).seconds / 3600  
    class Meta:
        verbose_name = "Permission Request"
        verbose_name_plural = "Permission Requests"


