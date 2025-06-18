from django.db import models

class Expenses(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
    ]

    TRAVEL_TYPE_CHOICES = [
        ('Flight', 'Flight'),
        ('Train', 'Train'),
        ('Bus', 'Bus'),
        ('Taxi', 'Taxi'),
        ('Own Vehicle', 'Own Vehicle'),
        ('Other', 'Other'),
    ]

    employee_user_id = models.IntegerField(null=True, blank=True) 
    emp_name = models.CharField(max_length=100, null=True, blank=True)  
    from_date = models.DateField(null=True, blank=True)  
    to_date = models.DateField(null=True, blank=True)  
    category = models.CharField(max_length=100, null=True, blank=True) 
    description = models.TextField(null=True, blank=True) 
    amount = models.IntegerField(null=True, blank=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, null=True, blank=True)  
    bills_upload = models.ImageField(upload_to='expense_bills/', null=True, blank=True)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', null=True, blank=True)  
    travel_type = models.CharField(max_length=20, choices=TRAVEL_TYPE_CHOICES, null=True, blank=True)  
    emp_department = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  

    def __str__(self):
        return f"{self.emp_name} - {self.category} - {self.amount}"
