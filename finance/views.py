import csv
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from .models import Payslip
from employees.models import Employee
from .serializers import PayslipSerializer
from rest_framework.response import Response
import pandas as pd
import csv
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from finance.models import Payslip  
import calendar


@csrf_exempt
def upload_payslip_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()

        # Read the uploaded file
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(uploaded_file, engine='openpyxl')  # Read xlsx
        else:
            return JsonResponse({'error': 'Unsupported file format. Please upload a CSV or Excel file.'}, status=400)

        # Convert to CSV format
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Process and save data to the database
        reader = csv.DictReader(csv_buffer)
        # print(reader)
        for row in reader:
            print(row)
            employee_id = row.get("Employee ID") or row.get("employee_id")
            employee_name = row.get("Employee Name") or row.get("employee_name")
            designation = row.get("designation") or row.get("Designation")
            company_name = row.get("Company Name") or row.get("company_name")
            place = row.get("Place") or row.get("place")
            salary = float(row.get("Salary") or row.get("salary", 0))
            month = row.get("Month") or row.get("month")
            status = row.get("Status") or row.get("status")
            department = row.get("department") or row.get("Department")
            # Basic logic to fill other columns
            basic_pay = salary * 0.5
            hra = salary * 0.25
            allowance = salary * 0.2
            tax = 200
            net = basic_pay + hra + allowance - tax
            
            doj = Employee.objects.get(employee_user_id = employee_id)
            print(doj)
            print(doj.date_of_joining)
            Payslip.objects.create(
                employee_id=employee_id,
                employee_name = employee_name,
                company_name = company_name,
                place = place,
                department = department,
                designation=designation,
                salary=salary,
                month=month,
                date_of_joining=doj.date_of_joining,
                status=status,
                basic_pay=basic_pay,
                house_rent_allowance=hra,
                fixed_allowance=allowance,
                professional_tax=tax,
                net_pay=net
            )

        return JsonResponse({'message': 'File uploaded and data saved successfully.'})

    return JsonResponse({'error': 'No file uploaded'}, status=400)


@api_view(['POST'])
def get_payslips(request):
    """
    POST: Filters payslips by year and/or month from JSON body.
    """
    year = request.data.get('year')
    month = request.data.get('month')

    records = Payslip.objects.all()

    def convert_month_to_number(month_str):
        if not month_str:
            return None
        month_str = month_str.strip().lower()
        for i in range(1, 13):
            if (calendar.month_name[i].lower() == month_str or
                calendar.month_abbr[i].lower() == month_str):
                return i
        return None

    # Try to convert month to number
    month_number = convert_month_to_number(month) if month else None

    if year and month_number:
        try:
            records = records.filter(month__year=year, month__month=month_number)
        except ValueError:
            return Response({"error": "Invalid year or month format."}, status=400)

    elif year:
        try:
            year = int(year)
            records = records.filter(month__year=year)
        except ValueError:
            return Response({"error": "Invalid year format."}, status=400)

    elif month_number:
        try:
            records = records.filter(month__month=month_number)
        except ValueError:
            return Response({"error": "Invalid month format."}, status=400)

    return Response(list(records.values()), status=200)


@api_view(['GET'])
def fetch_payslip_by_employee(request):
    if request.user.is_superuser:
        payslips = Payslip.objects.all()
    else:   
        employee = Employee.objects.get(user = request.user)
        print(employee.employee_user_id)
        try:
            payslips = Payslip.objects.filter(employee_id=employee.employee_user_id)
            if not payslips.exists():
                return Response({"error": "No transaction data found for this user."}, status=404)

        

        except Exception as e:
            return Response({"error": str(e)}, status=500)
    serializer = PayslipSerializer(payslips, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def get_latest_card_details(request):
    employee = Employee.objects.get(user = request.user)
    print(employee.employee_user_id)
    try:
        print(request)
        payslip = Payslip.objects.filter(employee_id=employee.employee_user_id).order_by('-id').first()
        
        if not payslip:
            return Response({"error": "No payslip found for this employee."}, status=404)
        
        salary = float(payslip.salary)
        
        tax_deduction = salary * 0.1  
        medical_insurance = salary * 0.02 
        net_salary = salary - (tax_deduction + medical_insurance)
        
        return Response({
            "employee_id": payslip.employee_id,
            "salary": salary,
            "tax_deduction": tax_deduction,
            "medical_insurance": medical_insurance,
            "net_salary": net_salary,
        }, status=200)
    
    except Exception as e:
        return Response({"error": str(e)}, status=500)