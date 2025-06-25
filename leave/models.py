from django.db import models
from employees.models import Employee  
from django.contrib.auth.models import User

class Leave(models.Model):
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

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    leave_id = models.AutoField(primary_key=True) 
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE, 
        related_name='leaves'  
    )
    fromDate = models.DateField()  
    toDate = models.DateField()
    leave_type = models.CharField(
        max_length=50,
        choices=LEAVE_TYPE_CHOICES,
        default='Sick Leave',
    )
    time_period = models.CharField(
        max_length=20,
        choices=TIME_PERIOD_CHOICES,
        default='fullDay',
    )
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    notify = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE, 
        related_name='notify'  
    )  
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
    )
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=20,blank=True, null=True) 
    user_department = models.CharField(max_length=20,blank=True, null=True)
    leave_days = models.FloatField()
    receiver_id = models.JSONField(default=list, blank=True, null=True)
    extra_days_worked = models.PositiveIntegerField(default=0)  
    paternity_days_taken = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    
    def __str__(self):
            return f"{self.employee.employee_first_name} {self.employee.employee_last_name}: {self.leave_type} ({self.fromDate} - {self.toDate})"

    def save(self, *args, **kwargs):
        if self.created_at:
            self.created_at = self.created_at.replace(microsecond=0)
        if self.updated_at:
            self.updated_at = self.updated_at.replace(microsecond=0)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"
    
    def total_days(self):
        return (self.toDate - self.fromDate).days + 1 

class LeaveBalance(models.Model):
    employee_id = models.IntegerField()
    cl_balance = models.FloatField(default=12)  
    ml_balance = models.FloatField(default=7)      
    lop = models.FloatField(default=0)
    comp_off = models.FloatField(default=0)
    paternity_balance = models.FloatField(default=2)
    onduty_exam = models.FloatField(default=7)
    onduty_official = models.FloatField(default=0)
    onduty_research =  models.FloatField(default=3)
    summer_vacation = models.FloatField(default=14)
    winter_vacation = models.FloatField(default=0)
    month_leave_taken = models.JSONField(default=dict)  
    user_name = models.CharField(max_length=20,blank=True, null=True) 
    userid  = models.IntegerField()
    def get_monthly_leave_taken(self, month):
        return self.month_leave_taken.get(str(month), 0)
    
    def calculate_balance(self, month):
        # This is where you handle the leave carry forward logic and LOP calculation
        cl_taken = sum(1 for leave in self.employee.leave_set.filter(leave_type='CL') if leave.from_date.month == month)
        ml_taken = sum(1 for leave in self.employee.leave_set.filter(leave_type='ML') if leave.from_date.month == month)

        if cl_taken > 3:
            lop = cl_taken - 3
            self.cl_balance -= lop
        if ml_taken > 3:
            lop = ml_taken - 3
            self.ml_balance -= lop

        # Carry forward logic
        self.month_leave_taken[str(month)] = cl_taken + ml_taken  # Track month-wise leave taken

        # Save the updated leave balances
        self.save()
