from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from .models import Employee, Attendance
from holiday.models import Holiday
from leave.models import Leave
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.utils.timezone import localtime, now
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg
from rest_framework.generics import UpdateAPIView
from employees_attendance.serializers import AttendanceSerializer

TRESTLE_API_URL = "https://api.trestle.com/face"
TRESTLE_API_KEY = "your_trestle_api_key_here"

@api_view(['POST'])
@permission_classes([AllowAny]) 
def register_face(request):
    """Register an employee's face with Trestle API."""
    employee_id = request.data.get('employee_id')
    # image = request.FILES.get('image')
    employee = get_object_or_404(Employee, user_id=employee_id)
    
    # response = requests.post(f"{TRESTLE_API_URL}/register", headers={"Authorization": f"Bearer {TRESTLE_API_KEY}"}, files={"image": image})
    
    # if response.status_code == 200:
    # face_id = response.json().get('face_id')
    face_id = request.data.get('face_id')
    employee.biometric = face_id
    print(face_id)
    employee.save()
    return Response({"message": "Face registered successfully", "face_id": face_id}, status=status.HTTP_201_CREATED)
    return Response({"error": "Face registration failed"}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def verify_face(request):
#     """Verify an employee's face for attendance."""
#     image = request.FILES.get('image')
#     response = requests.post(f"{TRESTLE_API_URL}/verify", headers={"Authorization": f"Bearer {TRESTLE_API_KEY}"}, files={"image": image})
    
#     if response.status_code == 200:
#         face_id = response.json().get('face_id')
#         employee = get_object_or_404(Employee, face_id=face_id)
        
#         Attendance.objects.create(employee=employee, status='Present')
#         return Response({"message": "Attendance marked successfully"}, status=status.HTTP_200_OK)
#     return Response({"error": "Face verification failed"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])  
def verify_face(request):
    """Verify a face and mark attendance."""
    employee_id = request.data.get('employee_id')
    employee = get_object_or_404(Employee, user_id=employee_id)
    if employee.biometric:
        current_time = localtime(now()).time()
        clock_in_str = current_time.strftime("%H:%M:%S")
        today = now().date()

        scheduled_start_time = datetime.strptime("09:00:00", "%H:%M:%S").time()
        late_by = datetime.combine(today, current_time) - datetime.combine(today, scheduled_start_time)
        late_by = late_by if current_time > scheduled_start_time else timedelta(0)  # No delay if on time
        
        last_attendance = Attendance.objects.filter(
            user_id=employee.user.id, date=today
        ).order_by('-id').first()  
        print(last_attendance)
        if not last_attendance:  
            Attendance.objects.create(
                user_id=employee.user.id,
                date=today,
                clock_in=clock_in_str,
                late_arrival=str(late_by).split(".")[0],
                user_name = request.user.username
            )
            return Response({
                "message": "Clock-in recorded successfully",
                "late_by": str(late_by).split(".")[0]
            }, status=status.HTTP_200_OK)

        if last_attendance.clock_out is None:  
            last_attendance.clock_out = clock_in_str  

            clock_in_time = datetime.combine(datetime.today(), last_attendance.clock_in)
            clock_out_time = datetime.combine(datetime.today(), current_time)
            working_hours = clock_out_time - clock_in_time
            last_attendance.working_hours = str(working_hours).split(".")[0]
            last_attendance.status = "Present"
            last_attendance.save()

            return Response({
                "message": "Clock-out recorded successfully",
                "working_hours": str(working_hours).split(".")[0]
            }, status=status.HTTP_200_OK)

        Attendance.objects.create(
            user_id=employee.user.id,
            date=today,
            clock_in=clock_in_str,
            late_arrival=str(late_by).split(".")[0],
        )
        return Response({
            "message": "New Clock-in recorded successfully",
            "late_by": str(late_by).split(".")[0]
        }, status=status.HTTP_200_OK)

    return Response({"error": "Face verification failed"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data(request):
    userid = request.user.id
    data = Attendance.objects.filter(user_id=userid).order_by('-date')
    print(data)
    response_data = []
    previous_weekend = None

    for record in data:
        formatted_date = record.date.strftime("%a, %d %B %Y")
        day_of_week = record.date.weekday()

        holiday = Holiday.objects.filter(date=record.date.day, month=record.date.strftime("%b")).first()
        is_holiday = bool(holiday)
        holiday_name = holiday.description if is_holiday else None

        leave = Leave.objects.filter(
            user_id=userid,
            fromDate__lte=record.date,
            toDate__gte=record.date
        ).first()
        is_on_leave = bool(leave)
        
        leave_type = leave.leave_type if is_on_leave else None
        if day_of_week in [5, 6]: 
            if previous_weekend:
                previous_weekend.append(record.date.strftime("%d %B"))
            else:
                previous_weekend = [record.date.strftime("%d %B")]
        else:
            if previous_weekend:
                response_data.append({
                    "date": f"Weekend {previous_weekend[0]} - {previous_weekend[-1]}" if len(previous_weekend) > 1 else f"Weekend {previous_weekend[0]}",
                    "isWeekend": True
                })
                previous_weekend = None

            response_data.append({
                "id": record.id,
                "date": formatted_date,
                "clockIn": record.clock_in.strftime("%H:%M") if record.clock_in else "--",
                "clockOut": record.clock_out.strftime("%H:%M") if record.clock_out else "--",
                "workingHours": f"{record.working_hours} hr" if record.working_hours else "--",
                "log": record.status,
                "isHoliday": is_holiday,
                "holidayName": holiday_name if is_holiday else None,
                "isOnLeave": is_on_leave,
                "leaveType": leave_type if is_on_leave else None,
                "status": "Holiday" if is_holiday else ("Leave" if is_on_leave else "Present"),
                "is_regularized": record.is_regularized,
                "approver": record.approver,
            })

    if previous_weekend:
        response_data.append({
            "date": f"Weekend {previous_weekend[0]} - {previous_weekend[-1]}" if len(previous_weekend) > 1 else f"Weekend {previous_weekend[0]}",
            "isWeekend": True
        })

    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_weekly_attendance(request):
    period = request.data.get('period', 'current_week')
    print(period)
    user_id = request.user.id  
    today = now().date()
    if period == 'current_week':
        print("current")
        start_date = today - timedelta(days=today.weekday())  
        end_date = start_date + timedelta(days=6)  
        grouping = 'date'
    elif period == 'last_week':
        start_date = today - timedelta(days=today.weekday() + 7)  
        end_date = start_date + timedelta(days=6)  
        grouping = 'date__week_day'
    elif period == 'current_month':
        start_date = today.replace(day=1)  
        end_date = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
        grouping = 'date__week_day'
    elif period == 'last_month':
        start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        end_date = (today.replace(day=1) - timedelta(days=1))
        grouping = 'date__week_day'
    else:
        return Response({"error": "Invalid period"}, status=400)

    attendance_data = Attendance.objects.filter(
        user_id=user_id,
        date__range=[start_date, end_date]
    )
    print(start_date, end_date)
    if period in ['current_week']:
        grouped_data = attendance_data.values('date').annotate(
            total_hours=Sum('working_hours')
        ).order_by('date')

        attendance_summary = []
        for record in grouped_data:
            total_seconds = float(record['total_hours']) if record['total_hours'] else 0
            
            total_seconds = min(total_seconds, 8 * 3600)

            formatted_hours = str(timedelta(seconds=int(total_seconds)))  
            attendance_summary.append({
                "day": record['date'].strftime("%A"),
                "date": record['date'].strftime("%Y-%m-%d"),
                "average_working_hours": formatted_hours
            })
        print(attendance_summary)

    else:
        grouped_data = attendance_data.values(grouping).annotate(
            average_hours=Avg('working_hours')
        ).order_by(grouping)

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        attendance_summary = []
        for record in grouped_data:
            weekday_index = record[grouping] - 2 if record[grouping] > 1 else 6
            average_seconds = float(record['average_hours']) if record['average_hours'] else 0
            
            average_seconds = min(average_seconds, 8 * 3600)
            
            formatted_hours = str(timedelta(seconds=int(average_seconds)))
            attendance_summary.append({
                "day": weekdays[weekday_index],
                "average_working_hours": formatted_hours
            })

    return Response(attendance_summary)


class SubmitRegularizationView(UpdateAPIView):
    def put(self, request, pk):
        try:
            attendance = Attendance.objects.get(pk=pk)

            if attendance.is_regularized:
                return Response({"message": "Already regularized"}, status=status.HTTP_400_BAD_REQUEST)

            attendance.regularization_reason = request.data.get("reason")
            attendance.regularization_status = "Pending"
            attendance.submit_regularize = True
            attendance.save()

            return Response({"message": "Regularization request submitted"}, status=status.HTTP_200_OK)

        except Attendance.DoesNotExist:
            return Response({"message": "Attendance record not found"}, status=status.HTTP_404_NOT_FOUND)


class ApproveRegularizationView(UpdateAPIView):
    def put(self, request, pk):
        try:
            attendance = Attendance.objects.get(pk=pk)
            print(request.data)
            approver = Employee.objects.get(employee_id=request.data.get("approved_by"))
            attendance.approver = approver.employee_first_name
            if attendance.regularization_status != "Pending":
                return Response({"message": "Request already processed"}, status=status.HTTP_400_BAD_REQUEST)

            attendance.approve_regularization(approver)
            return Response({"message": "Request approved successfully"}, status=status.HTTP_200_OK)

        except Attendance.DoesNotExist:
            return Response({"message": "Attendance record not found"}, status=status.HTTP_404_NOT_FOUND)


class RejectRegularizationView(UpdateAPIView):
    def put(self, request, pk):
        try:
            attendance = Attendance.objects.get(pk=pk)

            if attendance.regularization_status != "Pending":
                return Response({"message": "Request already processed"}, status=status.HTTP_400_BAD_REQUEST)

            attendance.reject_regularization()
            return Response({"message": "Request rejected successfully"}, status=status.HTTP_200_OK)

        except Attendance.DoesNotExist:
            return Response({"message": "Attendance record not found"}, status=status.HTTP_404_NOT_FOUND)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])       
def pending_regularize(request):
    attendance = Attendance.objects.filter(submit_regularize =True, regularization_status = "Pending")
    serializer = AttendanceSerializer(attendance, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])       
def get_regularize_data(request):
    attendance = Attendance.objects.filter(submit_regularize=True).exclude(regularization_status="Pending")
    serializer = AttendanceSerializer(attendance, many=True)
    return Response(serializer.data)