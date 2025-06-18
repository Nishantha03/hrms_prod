from django.urls import path
from .views import upload_payslip_file, get_payslips,fetch_payslip_by_employee, get_latest_card_details

urlpatterns = [
    path('upload-payslip/', upload_payslip_file, name='upload_payslip'),
    path('payslips/', get_payslips, name='get_payslips'),
    path('fetch_salary/', fetch_payslip_by_employee, name='fetch_payslip_by_employee'),
    path('salary_card/', get_latest_card_details, name='get_latest_card_details')

]
