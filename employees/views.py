from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Employee,Event
from .serializers import EmployeeSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from django.db.models.functions import ExtractDay, ExtractMonth
from rest_framework.decorators import api_view, permission_classes
from .utils import get_team
from datetime import datetime
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from employees_attendance.models import Attendance
from datetime import timedelta
from django.db.models import Sum
from django.db import IntegrityError
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd

import math


def is_nan(val):
    return isinstance(val, float) and math.isnan(val)

def clean_field(val):
    if val is None or is_nan(val):
        return ''
    val = str(val).strip()
    if val.lower().startswith('not available'):
        val = val.replace('Not Available', '').strip()
    if val.lower() == 'nan':
        return ''
    if val.lower() == 'None':
        return ''
    return val

def get_employee_display_name(employee):
    salutation = clean_field(getattr(employee, 'Salutation', ''))
    first_name = clean_field(getattr(employee, 'employee_first_name', ''))
    last_name = clean_field(getattr(employee, 'employee_last_name', ''))

    name_parts = [salutation, first_name, last_name]
    name = ' '.join(part for part in name_parts if part).strip()

    return name


class EventView(APIView):
    """
    API endpoint to process employee birthdays and work anniversaries
    if not already processed, and return all events with employee details.
    """

    def get(self, request):
        try:
            today = date.today()
            birthdays = Employee.objects.annotate(
                dob_day=ExtractDay('date_of_birth'),
                dob_month=ExtractMonth('date_of_birth')
            ).filter(dob_day=today.day, dob_month=today.month)
            for employee in birthdays:
                employee_name = f"{employee.Salutation} {employee.employee_first_name} {employee.employee_last_name}"
                
                Event.objects.update_or_create(
                    employee=employee,
                    event_type="Birthday",
                    event_date=today,
                    defaults={
                        "employee_name": get_employee_display_name(employee),
                        "employee_photo": employee.employee_photo,
                    },
                )

            # Handle work anniversaries using 'date_of_joining'
            work_anniversaries = Employee.objects.annotate(
                doj_day=ExtractDay('date_of_joining'),
                doj_month=ExtractMonth('date_of_joining')
            ).filter(doj_day=today.day, doj_month=today.month)
            for employee in work_anniversaries:
                Event.objects.update_or_create(
                    employee=employee,
                    event_type="Work Anniversary",
                    event_date=today,
                    defaults={
                        "employee_name": get_employee_display_name(employee),
                        "employee_photo": employee.employee_photo,
                    },
                )

            events = Event.objects.filter(event_date=today)

            event_data = [
                {
                    "employee_name": event.employee_name,
                    "employee_photo": event.employee_photo.url if event.employee_photo else None,
                    "event_type": event.event_type,
                    "event_date": event.event_date,
                }
                for event in events
            ]

            return Response(event_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
class EmployeeViewSet(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        if pk:
            try:
                employee = Employee.objects.get(user_id=pk, is_active=True)
                # print(employee)
                serializer = EmployeeSerializer(employee)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Employee.DoesNotExist:
                return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            employees = Employee.objects.filter(is_active=True)
            
            serializer = EmployeeSerializer(employees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        # print(request.data)
        data = request.data
        print(data)
        user_name = data['user']
        user_ = User.objects.get(username=user_name)
        print(user_)
        data['user'] = user_.id
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            employee = Employee.objects.get(employee_id=pk)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmployeeSerializer(employee, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_attendance_percentage(employee):
    if not employee.user:
        return 0.0 
    # print(employee)
    # print(employee.employee_id)
    total_worked_hours = Attendance.objects.filter(user_id=employee.employee_id, status="Present").aggregate(total_hours=Sum("working_hours"))["total_hours"] or 0  
    # print(total_worked_hours)

    if isinstance(total_worked_hours, timedelta):  
        worked_hours_float = total_worked_hours.total_seconds() / 3600  
    elif isinstance(total_worked_hours, (float, int)):
        worked_hours_float = float(total_worked_hours) 
    else:
        worked_hours_float = float(total_worked_hours) / 3600  

    expected_hours = 8 * 30

    if expected_hours == 0:
        return 0.0  

    return round((worked_hours_float / expected_hours) * 100, 2)

    
@api_view(['POST'])  
@permission_classes([IsAuthenticated])    
def deactivate(self,pk):
    try:
        employee = Employee.objects.get(employee_id=pk)
        employee.is_active = False
        employee.save() 
        return Response({"message": "Employee de-activated successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)   
    
    
def get_subordinates(manager):
    """
    Recursively fetch all subordinates of a given manager.
    """
    subordinates = Employee.objects.filter(reporting_manager = manager, is_active=True)
    result = []
    

    for emp in subordinates:
        result.append({
            "id": emp.employee_user_id,
            "name": get_employee_display_name(emp),
            "department": emp.departmant,
            "designation": emp.designation,
            "email": emp.email,
            "phone_number": emp.contact_number,
            "on_leave": emp.on_leave,
            "employee_photo": emp.employee_photo.url,
            "attendance_percentage": get_attendance_percentage(emp),
            "date_of_birth": emp.date_of_birth,
            "date_of_joining": emp.date_of_joining
            
        })
        # print(result)
        result.extend(get_subordinates(emp))

    return result
    
@api_view(['GET'])  
@permission_classes([IsAuthenticated])
def get_team_details(request):
    
    try:
        user = request.user
        # print(user)
        manager = Employee.objects.get(user=user, is_active = True) 
       
        team_members = [{
            "id": manager.employee_user_id,
            "name": get_employee_display_name(manager),
            "email": manager.email,
            "designation": manager.designation,
            "department": manager.departmant,
            "phone_number": manager.contact_number,
            "on_leave": manager.on_leave,
            "employee_photo": manager.employee_photo.url,
            "attendance_percentage": get_attendance_percentage(manager),
            "date_of_birth": manager.date_of_birth,
            "date_of_joining": manager.date_of_joining
        }]
        # print(team_members)
        team_members.extend(get_subordinates(manager))
        return Response(team_members, status=200) 
    except Employee.DoesNotExist:
        return Response({"error": "User is not an employee"}, status=404)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_celebrations(request):
    """
    Get birthdays and work anniversaries of the authenticated user's team.
    """
    team_response = get_team_details(request._request)  
    if team_response.status_code != 200: 
       return team_response 
    team_members = team_response.data 
    today = date.today()

    birthdays = []
    work_anniversaries = []

    for employee in team_members:
        if employee.get("date_of_birth"):
            try:
                dob = employee["date_of_birth"] if isinstance(employee["date_of_birth"], date) else datetime.strptime(employee["date_of_birth"], "%Y-%m-%d").date()
                if dob.day == today.day and dob.month == today.month:
                    birthdays.append({
                        "employee_name": employee["name"],
                        "employee_photo": employee["employee_photo"],
                        "event_type": "Birthday",
                        "event_date": today,
                    })
            except ValueError:
                pass  

        if employee.get("date_of_joining"):
            try:
                doj = employee["date_of_joining"] if isinstance(employee["date_of_joining"], date) else datetime.strptime(employee["date_of_joining"], "%Y-%m-%d").date()
                if doj.day == today.day and doj.month == today.month:
                    work_anniversaries.append({
                        "employee_name": employee["name"],
                        "employee_photo": employee["employee_photo"],
                        "event_type": "Work Anniversary",
                        "event_date": today,
                    })
            except ValueError:
                pass  
    return Response(birthdays + work_anniversaries, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_member_counts(request):
    """
    Count total team members and the number of team members on leave today.
    """
    try:
        team_response = get_team_details(request._request)
        
        if team_response.status_code != 200: 
            return team_response 
        team_members = team_response.data 
        # print(team_members)
        total_team_members = team_members.count() if isinstance(team_members, QuerySet) else len(team_members)
       
        today = date.today()
        
        on_leave_count = sum(1 for member in team_members if member.get("on_leave") == True)

        present_members = total_team_members - on_leave_count
        attendance_percentage = (present_members / total_team_members * 100) if total_team_members > 0 else 0
        absent_percentage = 100 - attendance_percentage
        ring_data = [
            {
                "name": "Present", 
                "value": round(attendance_percentage),
                "fill": "#87ceeb",
            }
        ]
        return Response([
            {
                "total_team_members": total_team_members,
                "team_members_on_leave": on_leave_count,
                "attendance_percentage": ring_data
            }],
            status=status.HTTP_200_OK,
        )
    except Employee.DoesNotExist:
        return Response(
            {"error": "Authenticated user is not an employee."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def build_org_chart(employee):
    
    employee_name = get_employee_display_name(employee)
    # print("**********after***EMP****");
    # print(employee_name);
    return {
        "id": employee.employee_user_id,
        "name": employee_name,
        "label":employee.designation,
        "department": employee.departmant,
        "profileimg": employee.employee_photo.url if employee.employee_photo else "/media/default-profile.png",
        "subordinates": [
            build_org_chart(subordinate) for subordinate in employee.subordinates.filter(is_active=True)
        ],
    }
    
def organizational_chart_view(request, employee_id=None):
    if employee_id:
        employee = get_object_or_404(Employee, id=employee_id)
    else:
        employee = Employee.objects.filter(reporting_manager__isnull=True, is_active = True).first()  

    if not employee:
        return JsonResponse({"error": "No employee found"}, status=404)
    org_chart = build_org_chart(employee)
    return JsonResponse([org_chart], safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employee_by_username(request, username):
    """
    Get employee details by username.
    """
    try:
        employee = get_object_or_404(Employee, user__username=username)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employee_by_id(request, pk):
    """
    Get employee details by id.
    """
    try:
        # print(pk)
        employee = get_object_or_404(Employee, user__id=pk)
        # print(employee)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
    

class UploadEmployeeExcelView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    hod_lookup = {}
    principal_user = None

    def post(self, request):
        file_path = request.FILES.get("file")
        # print(file_path)
        # file_path = r"C:\Santhiya\QPT\hrms_Updated_ april 07\backend\employees\emp_data_upload.xlsx"
        if not file_path:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:

            if file_path.name.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            # print(df)
            df.columns = df.columns.str.strip()
            for index, row in df.iterrows():
                username = row.get("username")
                password = row.get("password")
                # print(username, password)
                if not username or not password:
                    continue  # Skip if no username/password

                # Create or update user
                try:
                    user, created = User.objects.get_or_create(username=username)
                    if created:
                        user.email = row.get("email")
                        user.set_password(password)
                        
                    else:
                        if User.objects.filter(email=row.get("email")).exclude(username=username).exists():
                            print(f"User '{username}' already exists, skipping password update.")
                            continue
                        user.email = row.get("email")
                    user.is_active = True
                    user.save()
                except IntegrityError:
                    print(f"Skipping duplicate or invalid user: {username}")
                    continue

                # Create or update employee
                Employee.objects.update_or_create(
                    user=user,
                    defaults={
                        "employee_user_id": row.get("employee_user_id"),
                        "Salutation": row.get("Salutation"),
                        "employee_first_name": row.get("employee_first_name"),
                        "employee_last_name": row.get("employee_last_name"),
                        "email": row.get("email"),
                        "contact_number": row.get("contact_number"),
                        "date_of_birth": row.get("date_of_birth"),
                        "date_of_joining": row.get("date_of_joining"),
                        "gender": row.get("gender"),
                        "designation": row.get("designation"),
                        "departmant": row.get("departmant"),
                    },
                )
            
            hod_lookup = {}
            principal_user = None

            for _, row in df.iterrows():
                designation = str(row.get("designation", ""))
                department = str(row.get("departmant", ""))
                username = str(row.get("username", ""))

                if designation == "HOD"or designation == "Professor & HoD" or designation == "Associate Professor & HOD" or designation == "Dean":
                    hod_lookup[department] = username
                elif designation == "Principal":
                    principal_user = username

            # Step 3: Assign reporting managers
            for _, row in df.iterrows():
                designation = str(row.get("designation", ""))
                department = str(row.get("departmant", ""))
                username = str(row.get("username", ""))
                # print(designation,department,username)
                try:
                    user = User.objects.get(username=username)
                    # print(user)
                    employee = Employee.objects.get(user=user)
                    # print(employee)
                    if designation == "HOD"or designation == "Professor & HoD":
                        manager_username = principal_user
                    else:
                        manager_username = hod_lookup.get(department)
                    # print(hod_lookup)
                    # print(manager_username)
                    if manager_username:
                        try:
                            manager_user = User.objects.get(username=manager_username)
                            manager_user_id = manager_user.id
                            reporting_manager_emp = Employee.objects.get(user_id=manager_user_id)
                            employee.reporting_manager = reporting_manager_emp
                            employee.save()
                        except User.DoesNotExist:
                            continue
                except (User.DoesNotExist, Employee.DoesNotExist):
                    continue

            return Response({"message": "Employees and login details uploaded successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            excel_row_number = index + 2
            print(f"❌ Error at Excel row {excel_row_number}: {e}")
            import traceback
            return Response({
                "error": str(e),
                "trace": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

