from django.db import models

class Payslip(models.Model):
    employee_id = models.CharField(max_length=20, null=True, blank=True)
    employee_name = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    payslip_date = models.DateField(null=True, blank=True)
    salary = models.FloatField(null=True, blank=True)
    month = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=20, null=True, blank=True)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    house_rent_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fixed_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    worked_days = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("Paid", "Paid"), ("Pending", "Pending")])

    def __str__(self):
        return f"{self.employee_id} - {self.month} - {self.status}"
