from django.db import models
from django.contrib.auth.models import User

class Leave_admin(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('Casual Leave', 'Casual Leave'),
        ('Medical Leave', 'Medical Leave'),
        ('Comp Off', 'Comp Off'),
        ('On Duty Exam', 'On Duty exam'),
        ('On Duty Official', 'On Duty official'),
        ('On Duty Research', 'On Duty research'),
        ('Paternity Leave', 'Paternity Leave'),
        ('Summer Vacation', 'Summer Vacation'),
        ('Winter Vacation', 'Winter Vacation'),
    ]
    
    TIME_PERIOD_CHOICES = [
        ('fullDay', 'Full Day'),
        ('firstHalf', 'First Half'),
        ('secondHalf', 'Second Half'),
    ]
    
    leave_id = models.AutoField(primary_key=True)
    leave_id = models.IntegerField()
    fromDate = models.DateField()
    toDate = models.DateField()
    leave_type = models.CharField(
        max_length=50,
        choices=LEAVE_TYPE_CHOICES,
        default='Casual Leave',
    )
    time_period = models.CharField(
        max_length=20,
        choices=TIME_PERIOD_CHOICES,
        default='fullDay',
    )
    notes = models.TextField(blank=True, null=True)
    notify = models.CharField(max_length=100, blank=True, null=True)  # Employee Name (or email)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
    )
    reason = models.TextField(blank=True, null=True)
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=200, blank=True, null=True)
    user_department = models.CharField(max_length=20,blank=True, null=True)
    created_at = models.CharField(max_length=200, blank=True, null=True)
    updated_at = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.leave_type} from {self.fromDate} to {self.toDate}"

    

    class Meta:
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"


class Leave_admin_card(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('Medical Leave', 'Medical Leave'),
        ('Casual Leave', 'Casual Leave'),
        ('Annual Leave', 'Annual Leave'),
    ]
    
    TIME_PERIOD_CHOICES = [
        ('fullDay', 'Full Day'),
        ('firstHalf', 'First Half'),
        ('secondHalf', 'Second Half'),
    ]
    
    leave_id = models.AutoField(primary_key=True)
    leave_id = models.IntegerField()
    fromDate = models.DateField()
    toDate = models.DateField()
    leave_type = models.CharField(
        max_length=50,
        choices=LEAVE_TYPE_CHOICES,
        default='Casual Leave',
    )
    time_period = models.CharField(
        max_length=20,
        choices=TIME_PERIOD_CHOICES,
        default='fullDay',
    )
    notes = models.TextField(blank=True, null=True)
    notify = models.CharField(max_length=100, blank=True, null=True)  

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
    )
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=200, blank=True, null=True)
    user_department = models.CharField(max_length=20,blank=True, null=True)
    created_at = models.CharField(max_length=200, blank=True, null=True)
    updated_at = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.leave_type} from {self.fromDate} to {self.toDate}"

    

    class Meta:
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"