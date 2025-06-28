from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Leave,LeaveBalance
from .serializers import LeaveSerializer
from employees.models import Employee
from holiday.models import Holiday
from rest_framework.views import APIView
from datetime import datetime, timedelta
import calendar
from datetime import datetime, timedelta, date
import json
from django.db.models import Q
from dateutil.relativedelta import relativedelta
import re


class LeavesViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter leaves based on the logged-in user."""
        return Leave.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Override the create method to associate leave with the logged-in user."""
        serializer.save(user=self.request.user)
        
class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Override this method to restrict users to their own leave applications.
        """
        return Leave.objects.filter(user_id=self.request.user.id)

   

    @action(detail=True, methods=['post'])
    def approve_leave(self, request, pk=None):
        """
        Custom action to approve or reject leave by the reporting manager.
        """
        try:
            leave = Leave.objects.get(id=pk)
        except Leave.DoesNotExist:
            return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)

        # Assuming `approved_by` is a field in your Leave model (e.g., a ForeignKey to the manager)
        if request.user != leave.approved_by:
            return Response({'error': 'You are not authorized to approve this leave.'}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get('action')
        input(action)
        if action not in ['Approved', 'Rejected']:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = action  # Assuming status is the field representing the approval state
        leave.save()  
        

        return Response({'message': f'Leave {action}'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_leave_data(self, request):
        """
        Custom action to get leave data for the authenticated user.
        """
        
        leave_data = Leave.objects.all()
       
        serialized_leave_data = LeaveSerializer(leave_data, many=True)
        return Response(serialized_leave_data.data)
    @action(detail=False, methods=['get'])
    def get_user_leave(self, request, pk=None):
        """
        Custom action to get leave data for the authenticated user.
        """       
        leave_data = Leave.objects.filter(user_id= pk).order_by('-leave_id')
        print(leave_data)
        serialized_leave_data = LeaveSerializer(leave_data, many=True)
        return Response(serialized_leave_data.data)
    
    @action(detail=False, methods=['delete'])
    def delete_leave_by_values(self, request, pk=None):
        """
        Custom action to delete a leave application by matching all provided field values.
        """
        
        
        try:
            # Filter the Leave records that match all the provided fields
            leave = Leave.objects.get(leave_id=pk)

           
            if not leave:
                return Response({'error': 'Leave record not found.'}, status=status.HTTP_404_NOT_FOUND)

            # print(request.user.is_staff)
            # if not request.user.is_staff:
            #     return Response({'detail': 'You are not authorized to delete this leave.'}, status=status.HTTP_403_FORBIDDEN)
            

            # Delete the leave record
            leave.delete()

            return Response({'message': 'Leave application deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

   
    @action(detail=True, methods=['get'])
    def get_leave_detail(self, request, pk=None):
        """
        Custom action to get the leave details for a specific leave by its ID.
        """

        try:
            leave = Leave.objects.get(leave_id=pk)
        except Leave.DoesNotExist:
            return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)

        serialized_leave_data = LeaveSerializer(leave)
        return Response(serialized_leave_data.data)


    @action(detail=False, methods=['post'])
    def submit_leave_form(self, request):
        """
        Custom action to submit a leave application form.
        Accepts leave details and creates a new leave record.
        """
        data = request.data
        from_process_date = datetime.strptime(data['fromDate'], "%Y-%m-%d")
        to_process_date = datetime.strptime(data['toDate'], "%Y-%m-%d")
        current_date = datetime.now()
        
        if from_process_date.date() < current_date.date() or to_process_date.date() < current_date.date():
            return Response({
                "error": "Leave cannot be applied for past dates.",
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if  (from_process_date.weekday() == 6 and to_process_date .weekday() == 6) or (from_process_date == datetime(2024, 12, 25) and to_process_date == datetime(2024, 12, 25)):
            return Response({
                "error": "Leave cannot be applied on Holidays.",
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_name = data.get('user_name', '').strip()

            if not user_name:
                return Response({"error": "User name is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Normalize names like "Dr.Saranya" → "Dr. Saranya"
            user_name = re.sub(r'^(Mr|Mrs|Ms|Dr)\.?(?=\w)', r'\1. ', user_name)

            # Split into parts
            parts = user_name.split()

            # Supported salutations
            salutations = ['Mr.', 'Mrs.', 'Ms.', 'Dr.']

            # Extract components
            salutation = ''
            first_name = ''
            last_name = ''

            if parts and parts[0] in salutations:
                salutation = parts[0]
                if len(parts) >= 2:
                    first_name = parts[1]
                if len(parts) >= 3:
                    last_name = " ".join(parts[2:])
            else:
                if len(parts) >= 1:
                    first_name = parts[0]
                if len(parts) >= 2:
                    last_name = " ".join(parts[1:])

            filters = {}
            if salutation:
                filters['Salutation__iexact'] = salutation
            if first_name:
                filters['employee_first_name__iexact'] = first_name
            if last_name:
                filters['employee_last_name__iexact'] = last_name

            employee = Employee.objects.filter(**filters).first()
            print("Employee Leave", employee);
        except Employee.DoesNotExist:
            return Response({
                "error": "Employee not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Validate leave type restrictions based on joining date
        joining_date = employee.date_of_joining  # Make sure this field exists in your model

        if data['leave_type'] == 'Casual Leave':
            next_month_date = (joining_date.replace(day=1) + relativedelta(months=1))
            if from_process_date.date() < next_month_date:
                return Response({
                    "error": "Casual Leave can be applied only from the next month after the joining date."
                }, status=status.HTTP_400_BAD_REQUEST)

        elif data['leave_type'] == 'Medical Leave':
            two_years_after_joining = joining_date + relativedelta(years=2)
            if from_process_date.date() < two_years_after_joining:
                return Response({
                    "error": "Medical Leave can be applied only after 2 years from the joining date."
                }, status=status.HTTP_400_BAD_REQUEST)
        if data['leave_type'].startswith('On Duty'):
            receiver_ids = []
            current_manager = employee.reporting_manager
            while current_manager :
                receiver_ids.append(current_manager.user.id)
                current_manager = current_manager.reporting_manager
            data['receiver_id'] = receiver_ids
        else:
            data['receiver_id'] = [employee.reporting_manager.user.id] if employee.reporting_manager else []
        
        employee_id = employee.employee_id
        notify_emp = Employee.objects.get(employee_first_name = data['notify']) 
        notify_id = notify_emp.employee_id
        data['employee'] = employee_id
        data['notify'] = notify_id
        print(data)
        total_leave_days = 0
        current_date  = from_process_date.date()
        to_date = to_process_date.date()
        time_period = data['time_period']
        holiday_queryset = Holiday.objects.all()
        holidays = [(holiday.day, holiday.month) for holiday in holiday_queryset]
        while current_date <= to_date:
            # Check if the current day is not a Sunday and not a holiday
            is_sunday = current_date.weekday() == 6
            is_holiday = (current_date.day, current_date.month) in holidays
            
            if not is_sunday and not is_holiday:
                if time_period in ['firstHalf', 'secondHalf']:
                    total_leave_days += 0.5
                else:
                    total_leave_days += 1
            current_date += timedelta(days=1)
        data['leave_days'] = total_leave_days 
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            leave = serializer.save(user_id=request.user.id)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)  
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def update_leave(self, request, pk=None):
        """
        Custom action to update an existing leave application.
        """
        try:
            leave = Leave.objects.get(leave_id=pk)
        except Leave.DoesNotExist:
            return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)

        if leave.user_id != request.user.id and not request.user.is_staff:
            return Response({'error': 'You are not authorized to update this leave.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = LeaveSerializer(leave, data=request.data, partial=True)  # partial=True allows updating specific fields
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def approve_leave(self, request, pk=None):
        try:
            leave_request = Leave.objects.get(leave_id=pk)
            new_status = request.data.get("status")
            new_reason = request.data.get("reason")
            old_status = leave_request.status 
            print(old_status)
            
            if new_status in ["Approved", "Rejected"]:
                leave_request.status = new_status
                leave_request.reason = new_reason
                leave_request.save()
                monthly_limit = 3.0 
                ml_monthly_limit = 7.0
                pl_limit = 2.0
                onduty_exam_limit = 7.0
                onduty_research_limit = 3.0
                summer_vacation_limit = 14.0
                
                print("***************")
                if old_status == 'Approved' and new_status == 'Rejected':
                    employee_id = leave_request.employee.employee_id
                    total_leave_days = leave_request.leave_days
                    from_process_date = leave_request.fromDate
                    month_name = calendar.month_name[from_process_date.month]

                    try:
                        leave_balance = LeaveBalance.objects.get(employee_id=employee_id)
                    except LeaveBalance.DoesNotExist:
                        return Response({'error': 'Leave balance not found for employee'}, status=status.HTTP_404_NOT_FOUND)

                    # Parse month_leave_taken
                    if isinstance(leave_balance.month_leave_taken, str):
                        leave_usage = json.loads(leave_balance.month_leave_taken)
                    elif isinstance(leave_balance.month_leave_taken, dict):
                        leave_usage = leave_balance.month_leave_taken
                    else:
                        leave_usage = {}

                    if month_name in leave_usage:
                        if leave_request.leave_type == 'Casual Leave':
                            cl_days_used = min(total_leave_days, monthly_limit)  # CL days capped at the monthly limit
                            lop_days_used = total_leave_days - cl_days_used  # Remaining days deducted as LOP
                            print(cl_days_used, lop_days_used)
                            leave_balance.cl_balance += cl_days_used
                            
                            leave_balance.lop = max(0, leave_balance.lop - lop_days_used)
                            
                            # Adjust the leave usage record for the month
                            leave_usage[month_name]['CL'] = max(0.0, leave_usage[month_name]['CL'] - total_leave_days)
                            
                        elif leave_request.leave_type == 'Medical Leave':
                            ml_days_used = min(total_leave_days, ml_monthly_limit)  # CL days capped at the monthly limit
                            lop_days_used = total_leave_days - ml_days_used  # Remaining days deducted as LOP
                            print(ml_days_used, lop_days_used)
                            leave_balance.ml_balance += ml_days_used
                            
                            leave_balance.lop = max(0, leave_balance.lop - lop_days_used)
                            
                            # Adjust the leave usage record for the month
                            leave_usage[month_name]['ML'] = max(0.0, leave_usage[month_name]['ML'] - total_leave_days)

                        elif leave_request.leave_type == 'Paternity Leave':
                            paternity_days_used = min(total_leave_days, pl_limit)
                            lop_days_used = total_leave_days - paternity_days_used

                            leave_balance.paternity_balance -= paternity_days_used
                            leave_balance.lop = max(0, leave_balance.lop - lop_days_used)

                            leave_usage[month_name]['PL'] = max(0.0, leave_usage[month_name].get('PL', 0) - total_leave_days)
                        
                        elif leave_request.leave_type == 'On Duty exam':
                            exam_days_used = min(total_leave_days, onduty_exam_limit)
                            lop_days_used = total_leave_days - exam_days_used

                            leave_balance.onduty_exam -= exam_days_used
                            leave_balance.lop = max(0, leave_balance.lop - lop_days_used)

                            leave_usage[month_name]['OD_E'] = max(0.0, leave_usage[month_name].get('OD_E', 0) - total_leave_days)
                        
                        elif leave_request.leave_type == 'On Duty research':
                            research_days_used = min(total_leave_days, onduty_research_limit)
                            lop_days_used = total_leave_days - research_days_used

                            leave_balance.onduty_research -= research_days_used
                            leave_balance.lop = max(0, leave_balance.lop - lop_days_used)

                            leave_usage[month_name]['OD_R'] = max(0.0, leave_usage[month_name].get('OD_R', 0) - total_leave_days)
                        
                        elif leave_request.leave_type == 'Summer Vacation':
                            summer_days_used = min(total_leave_days, summer_vacation_limit)
                            lop_days_used = total_leave_days - summer_days_used

                            leave_balance.summer_vacation -= summer_days_used
                            leave_balance.lop = max(0, leave_balance.lop - lop_days_used)

                            leave_usage[month_name]['SV'] = max(0.0, leave_usage[month_name].get('SV', 0) - total_leave_days)      
                    
                        elif leave_request.leave_type == 'Comp Off':
                            leave_balance.lop = max(0, leave_balance.lop - total_leave_days)
                            leave_balance.cl_balance += total_leave_days 

                            leave_usage[month_name]['comp_off'] = leave_usage[month_name].get('comp_off', 0) + total_leave_days

                        elif leave_request.leave_type == 'On Duty official':
                            leave_balance.onduty_official += total_leave_days 

                            leave_usage[month_name]['OD_O'] = leave_usage[month_name].get('OD_O', 0) + total_leave_days

                        elif leave_request.leave_type == 'Winter Vacation':
                            leave_balance.winter_vacation += total_leave_days  

                            leave_usage[month_name]['winter_vacation'] = leave_usage[month_name].get('winter_vacation', 0) + total_leave_days

                       
                    # Save the updated leave balance and usage
                    leave_balance.month_leave_taken = json.dumps(leave_usage)
                    leave_balance.save()

                    # Update employee's `on_leave` status
                    employee = leave_request.employee
                    if employee.on_leave and leave_request.fromDate <= date.today() <= leave_request.toDate:
                        employee.on_leave = False
                        employee.save()

                    return Response({'message': 'Leave rejected and leave balance reverted.'}, status=status.HTTP_200_OK)
                
                elif new_status == 'Approved':
                    
                    employee_id = leave_request.employee.employee_id
                    from_process_date = leave_request.fromDate
                    to_process_date = leave_request.toDate
                    employee = leave_request.employee 
                    if from_process_date <= date.today() <= to_process_date:
                        employee.on_leave = True
                    else:
                        employee.on_leave = False
                    employee.save()
                    
                    total_leave_days = leave_request.leave_days
                    print("Leave_days", total_leave_days)
                    try:
                        leave_balance = LeaveBalance.objects.get(employee_id=employee_id)
                    except LeaveBalance.DoesNotExist:
                        return Response({'error': 'Leave balance not found for employee'}, status=status.HTTP_404_NOT_FOUND)

                    if isinstance(leave_balance.month_leave_taken, str):
                        leave_usage = json.loads(leave_balance.month_leave_taken)
                    elif isinstance(leave_balance.month_leave_taken, dict):
                        leave_usage = leave_balance.month_leave_taken
                    else:
                        leave_usage = {}
                    print("Parsed month_leave_taken:", leave_usage)
                    month_name = calendar.month_name[from_process_date.month]

                    if (month_name not in leave_usage) :
                        leave_usage[month_name] = {'CL': 0.0, 'ML': 0.0, 'OD_O': 0.0, 
                                                   'winter_vacation': 0.0, 'PL':0.0, 'OD_E':0.0,
                                                   'SV': 0.0, 'OD_R':0.0
                                                   }
                    
                    total_leave_days = leave_request.leave_days
                    print(leave_usage)
                
                    if leave_request.leave_type == 'Casual Leave':
                        print("Before CL Update:", leave_usage[month_name]['CL'], total_leave_days)
                        leave_usage[month_name]['CL'] += total_leave_days
                        if leave_usage[month_name]['CL'] <= monthly_limit:
                            leave_balance.cl_balance -= total_leave_days
                        else:
                            cl_days = max(0, monthly_limit - (leave_usage[month_name]['CL'] - total_leave_days))
                            lop_days = total_leave_days - cl_days
                            leave_balance.cl_balance -= cl_days
                            leave_balance.lop += lop_days

                    elif leave_request.leave_type == 'Medical Leave':
                        leave_usage[month_name]['ML'] += total_leave_days
                        if leave_usage[month_name]['ML'] <= ml_monthly_limit:
                            leave_balance.ml_balance -= total_leave_days
                        else:
                            ml_days = max(0, ml_monthly_limit - (leave_usage[month_name]['ML'] - total_leave_days))
                            lop_days = total_leave_days - ml_days
                            leave_balance.ml_balance -= ml_days
                            leave_balance.lop += lop_days
                    
                    elif leave_request.leave_type == 'Paternity Leave':
                        leave_usage[month_name]['PL'] += total_leave_days
                        if leave_usage[month_name]['PL'] <= pl_limit:
                            leave_balance.paternity_balance -= total_leave_days
                        else:
                            pl_days = max(0, pl_limit - (leave_usage[month_name]['PL'] - total_leave_days))
                            lop_days = total_leave_days - pl_days
                            leave_balance.ml_balance -= pl_days
                            leave_balance.lop += lop_days
                    
                    elif leave_request.leave_type == 'On Duty Exam':
                        leave_usage[month_name]['OD_E'] += total_leave_days
                        if leave_usage[month_name]['OD_E'] <= onduty_exam_limit:
                            leave_balance.onduty_exam -= total_leave_days
                        else:
                            od_e_days = max(0, onduty_exam_limit - (leave_usage[month_name]['OD_E'] - total_leave_days))
                            lop_days = total_leave_days - od_e_days
                            leave_balance.ml_balance -= od_e_days
                            leave_balance.lop += lop_days
                    
                    elif leave_request.leave_type == 'On Duty Research':
                        leave_usage[month_name]['OD_R'] += total_leave_days
                        if leave_usage[month_name]['OD_R'] <= onduty_research_limit:
                            leave_balance.onduty_research -= total_leave_days
                        else:
                            od_r_days = max(0, onduty_research_limit - (leave_usage[month_name]['OD_R'] - total_leave_days))
                            lop_days = total_leave_days - od_r_days
                            leave_balance.ml_balance -= od_r_days
                            leave_balance.lop += lop_days
                    
                    elif leave_request.leave_type == 'Summer Vacation':
                        leave_usage[month_name]['SV'] += total_leave_days
                        if leave_usage[month_name]['SV'] <= summer_vacation_limit:
                            leave_balance.summer_vacation -= total_leave_days
                        else:
                            sv_days = max(0, summer_vacation_limit - (leave_usage[month_name]['SV'] - total_leave_days))
                            lop_days = total_leave_days - pl_days
                            leave_balance.summer_vacation -= sv_days
                            leave_balance.lop += lop_days
                    
                    elif leave_request.leave_type == 'Comp Off':
                        leave_usage[month_name]['comp_off'] += total_leave_days
                        leave_balance.comp_off += total_leave_days
                    
                    elif leave_request.leave_type == 'On Duty Official':
                        leave_usage[month_name]['OD_O'] += total_leave_days
                        leave_balance.onduty_official += total_leave_days
                    
                    elif leave_request.leave_type == 'Winter Vacation':
                        leave_usage[month_name]['winter_vacation'] += total_leave_days
                        leave_balance.winter_vacation += total_leave_days
                    
                    leave_balance.month_leave_taken = json.dumps(leave_usage)
                    print("After Update:", leave_balance.cl_balance, leave_balance.ml_balance, leave_balance.month_leave_taken)

                    leave_balance.save()

                    return Response({'message': f'Leave {action} and leave balance updated.'}, status=status.HTTP_200_OK)
                return Response({"message": "Status updated successfully"}, status=status.HTTP_200_OK)
            
            else:
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        except Leave.DoesNotExist:
            return Response({"error": "Leave request not found"},status=status.HTTP_400_BAD_REQUEST)
        


    
class LeaveCountView(APIView):
    def get(self, request, pk=None):
        employee = Employee.objects.get(user_id = pk) 
        onleave_today = Leave.objects.filter(
            user_id=pk,
            fromDate__lte=date.today(),
            toDate__gte=date.today(),
            status='Approved'
            ).exists()
        
        if onleave_today:
            if not employee.on_leave:
                employee.on_leave = True
                employee.save()
                print("Leave started. Status updated to True.")
        else:
            if employee.on_leave:
                employee.on_leave = False
                employee.save()
                print("Leave ended. Status updated to False.")
        leave_balance, created = LeaveBalance.objects.get_or_create(
            employee_id=employee.employee_id,
            defaults={
                'cl_balance': 12,
                'ml_balance': 7,
                'month_leave_taken': {},
                'lop': 0,
                'comp_off':0,
                'paternity_balance': 2,
                'onduty_exam': 7,
                'onduty_official': 0,
                'onduty_research': 3,
                'summer_vacation': 14,
                'winter_vacation': 0,
                'userid': request.user.id,
            }
        )
        try:
            leave_balance = LeaveBalance.objects.get(userid=pk)
            return Response({
                'cl': leave_balance.cl_balance,
                'ml': leave_balance.ml_balance,
                'lop': leave_balance.lop,
                'comp_off': leave_balance.comp_off,
                'paternity_balance': leave_balance.paternity_balance,
                'onduty_exam': leave_balance.onduty_exam,
                'onduty_official': leave_balance.onduty_official,
                'onduty_research': leave_balance.onduty_research,
                'summer_vacation': leave_balance.summer_vacation,
                'winter_vacation': leave_balance.winter_vacation,
            })
        except LeaveBalance.DoesNotExist:
            return Response({'error': 'Leave balance not found for this employee.'}, status=404)
        

class LeavePrevView(APIView):
    def post(self, request):
        """
        Preview the leave impact before submitting the form.
        Returns: Total applied days, CL deduction, and LOP deduction.
        """
        data = request.data
        print(data)
        user_id = request.user.id
        # input(user_id)
        from_date = datetime.strptime(data['fromDate'], "%Y-%m-%d").date()
        to_date = datetime.strptime(data['toDate'], "%Y-%m-%d").date()
        time_period = data['time_period']
        leave_type = data['leave_type']

        if from_date > to_date:
            return Response({'error': 'Invalid date range'}, status=400)

        # Fetch Employee
        try:
            employee = Employee.objects.get(user=user_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)

        # Fetch Leave Balance
        leave_balance, created = LeaveBalance.objects.get_or_create(
            employee_id=employee.employee_id,
            defaults={
                'cl_balance': 12,
                'ml_balance': 7,
                'month_leave_taken': {},
                'lop': 0,
                'comp_off': 0,
                'paternity_balance': 2,
                'onduty_exam': 7,
                'onduty_official': 0,
                'onduty_research': 3,
                'summer_vacation': 14,
                'winter_vacation': 0,
                'userid': request.user.id,
            }
        )
        
        leave_limits = {
            'Casual Leave': 3.0,
            'Medical Leave': 7.0,
            'Paternity Leave': 2.0,
            'On Duty Exam': 7.0,
            'On Duty Official': float('inf'),
            'On Duty Research': 3.0,
            'Summer Vacation': 14.0,
            'Winter Vacation':  float('inf'),
            'Comp Off': float('inf')
        }
        
        holidays = {(h.day, h.month) for h in Holiday.objects.all()}
        
        total_days = 0
        current_date = from_date
        while current_date <= to_date:
            is_sunday = current_date.weekday() == 6
            is_holiday = (current_date.day, current_date.month) in holidays
            
            if not is_sunday and not is_holiday:
                if time_period in ['firstHalf', 'secondHalf']:
                    total_days += 0.5
                else:
                    total_days += 1
            current_date += timedelta(days=1)

        # Get month leave taken
        month_name = calendar.month_name[from_date.month]
        leave_usage = json.loads(leave_balance.month_leave_taken or "{}")
        # inp/ut(leave_usage)
        if month_name not in leave_usage:
            leave_usage[month_name] = {lt[:2]: 0.0 for lt in leave_limits.keys()}
        deductions = {
            'total_leave_days': total_days,
            'lop_deduction': 0,
            'cl_deduction': 0,
            'ml_deduction': 0,
            'comp_off': 0,
            'paternity_deduction': 0,
            'onduty_exam_deduction': 0,
            'onduty_official_deduction': 0,
            'onduty_research_deduction': 0,
            'summer_vacation_deduction': 0,
            'winter_vacation_deduction': 0,
        }
        specific_leave_balance = 0
        if leave_type == 'Casual Leave':
            specific_leave_balance = leave_balance.cl_balance
        elif leave_type == 'Medical Leave':
            specific_leave_balance = leave_balance.ml_balance
        elif leave_type == 'Paternity Leave':
            specific_leave_balance = leave_balance.paternity_balance
        elif leave_type == 'On Duty Exam':
            specific_leave_balance = leave_balance.onduty_exam
        elif leave_type == 'On Duty Official':
            specific_leave_balance = leave_balance.onduty_official
        elif leave_type == 'On Duty Research':
            specific_leave_balance = leave_balance.onduty_research
        elif leave_type == 'Summer Vacation':
            specific_leave_balance = leave_balance.summer_vacation
        elif leave_type == 'Winter Vacation':
            specific_leave_balance = leave_balance.winter_vacation
        elif leave_type == 'Comp Off':
            specific_leave_balance = leave_balance.comp_off
            
        if leave_type in leave_limits:
            print(leave_type)
            leave_key = leave_type.lower().replace(' ', '_') + '_deduction'
            leave_used = leave_usage[month_name].get(leave_type[:2], 0.0)
            leave_available = max(0, leave_limits[leave_type] - leave_used)
            print(leave_key, leave_used, leave_available)
            if total_days <= leave_available:
                deductions[leave_key] = total_days
            else:
                deductions[leave_key] = leave_available
                deductions['lop_deduction'] = total_days - leave_available

       

        else:
            return Response({'error': 'Invalid leave type'}, status=400)
        response_data = {
            **{k: v for k, v in deductions.items() if v > 0 or k == 'total_leave_days'},
            'leave_type': leave_type,
            'leave_balance': specific_leave_balance  
        }
        print(response_data)
        return Response([response_data], status=200)



@api_view(['GET'])
def get_pending_leave(request):
    """
    Get pending leave details for the employee and send data based on hierarchy.
    """
    user = request.user
    print(user)
    try:
        leaves = Leave.objects.filter(
            Q(receiver_id__contains=[user.id]) & Q(status="Pending")
        )
        
        serialized_leave_data = LeaveSerializer(leaves, many=True).data
        return Response(serialized_leave_data)

    except Leave.DoesNotExist:
        return Response({'error': 'Leave not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
