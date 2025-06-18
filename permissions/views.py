from datetime import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Permission, Employee
from permissions.serializers import PermissionSerializer
from rest_framework.decorators import action
from datetime import datetime, time, timedelta, date


class PermissionRequestViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def submit_form(self, request):
        """
        Custom action to submit a permission request.
        """
        data = request.data
        print(data)
        
        session = data.get('session')
        duration = data.get('duration')
        if session not in ['FN', 'AN'] or duration not in ['1', '2']:
            return Response({
                "error": "Invalid session or duration. Session must be 'FN' or 'AN', and duration must be '1hr' or '2hr'."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start_time = None
        end_time = None
        
        if session == 'FN':
            start_time = time(8, 40)
            if duration == '1':
                end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=1)).time()
            elif duration == '2':
                end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=2)).time()
        elif session == 'AN':
            if duration == '1':
                start_time = time(15, 10)
                end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=1)).time()
            elif duration == '2':
                start_time = time(14, 10)
                end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=2)).time()
        
        data['time_from'] = start_time.strftime("%H:%M")
        data['time_to'] = end_time.strftime("%H:%M")    
        
        employee = Employee.objects.get(employee_first_name=data['user_name'])
        employee_id = employee.employee_id
        data['employee'] = employee_id
        print(data)
        
        process_date = datetime.strptime(data['date'], "%Y-%m-%d")
        if  process_date.weekday() == 6 or process_date == datetime(2024, 12, 25) :
            return Response({
                "error": "Leave cannot be applied on Holidays.",
            }, status=status.HTTP_400_BAD_REQUEST)
        time_from = datetime.strptime(data['time_from'], "%H:%M")
        time_to = datetime.strptime(data['time_to'], "%H:%M")
        
        present_time = datetime.now()
        current_time = present_time.time()
        current_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        print(current_date, date.today())
        
        if (current_date == date.today()):
            print("*****")
            if (time_from.time() < current_time or time_to.time() < current_time):
                print("&&&&777")
                return Response(
                    {"error": "Applied hours must be in the future."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif current_date != date.today():
            return Response(
                {"error": "Cannot apply for future."},
                status=status.HTTP_400_BAD_REQUEST
                )
        existing_permission = Permission.objects.filter(
            employee=data['employee'], 
            date=process_date
        ).first()

        if existing_permission:
            existing_session = existing_permission.session  
            if existing_session == session:
                return Response({
                    "error": f"Permission already applied for {session} on this date."
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "error": "Cannot apply permission for both FN and AN on the same day."
                }, status=status.HTTP_400_BAD_REQUEST)
        from_hour = time_from.hour
        from_minute = time_from.minute
        to_hour = time_to.hour
        to_minute = time_to.minute

        applied_hours = (to_hour + to_minute / 60) - (from_hour + from_minute / 60)
        if applied_hours < 0.5:
            return Response(
                {"error": "Permission duration must be at least half an hour."},
                status=status.HTTP_400_BAD_REQUEST
            )
        data['leave_balance'] = applied_hours
        permission = Permission.objects.filter(employee=data['employee']).first()
    
        if permission:
            avail_hours = permission.avail_permission

            # Check if applied hours are less than or equal to available hours
            if applied_hours <= avail_hours:
                # Proceed with saving the permission request
                serializer = PermissionSerializer(data=request.data)
                if serializer.is_valid():
                    # Save the permission request
                    serializer.save()

                    # Update the available leave balance (subtract the applied hours)
                    permission.avail_permission = avail_hours - applied_hours
                    permission.save()

                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Return an error if applied hours are greater than available leave
                return Response(
                    {"error": "Insufficient leave balance. Please contact HR."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        elif permission is None:
            
            serializer = PermissionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "No permission record found for the employee."},
                status=status.HTTP_404_NOT_FOUND
            )

    
    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        """
        Custom action to update the status of a permission request.
        If approved, deduct the applied hours from the leave balance.
        """
        try:
            permission = Permission.objects.get(permission_id = pk)
            data = request.data
            status_update = data.get("status", "").lower()

            if status_update not in ["approved", "rejected"]:
                return Response({"error": "Invalid status. Status must be 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

            # If approved, update the leave balance
            if status_update == "approved":
                # time_from = permission.time_from
                # time_to = permission.time_to

                # from_hour = time_from.hour
                # from_minute = time_from.minute
                # to_hour = time_to.hour
                # to_minute = time_to.minute

                # applied_hours = (to_hour + to_minute / 60) - (from_hour + from_minute / 60)

                # # approved_permissions = Permission.objects.filter(
                # #     employee_id=employee.employee_id,
                # #     status="approved"
                # # )
                # # input(approved_permissions)
                # # Check leave balance
                # employee = permission.employee
                # user_leave_balance = Permission.objects.filter(employee_id=employee.employee_id).last().leave_balance \
                #                     if Permission.objects.filter(employee_id=employee.employee_id).exists() else 2.0

                # if applied_hours > user_leave_balance:
                #     return Response({"error": "Insufficient leave balance."}, status=status.HTTP_400_BAD_REQUEST)

                # # Deduct applied hours
                # new_balance = user_leave_balance - applied_hours
                # permission.leave_balance = new_balance
                permission.status = "approved"
                permission.save()

                return Response({
                    "message": "Permission request approved successfully.",
                    # "leave_balance": new_balance,
                }, status=status.HTTP_200_OK)

            # If rejected, just update the status
            if status_update == "rejected":
                permission.status = "rejected"
                permission.notes = data.get("notes")
            permission.save()
            return Response({
                "message": "Permission request rejected successfully.",
            }, status=status.HTTP_200_OK)

        except Permission.DoesNotExist:
            return Response({"error": "Permission not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, pk=None):
        """
        Handle GET requests to retrieve all permission records for the logged-in user.
        """
        permissions = Permission.objects.filter(user_id=pk)
        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_permission(self, request):
        permissions = Permission.objects.all()
        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Handle DELETE requests to remove permission records by employee ID.
        """
        try:
            
            permissions = Permission.objects.filter(permission_id=pk)

            if not permissions.exists():
                return Response({"error": "No permission records found for the given employee ID."}, status=status.HTTP_404_NOT_FOUND)

            permissions.delete()
            return Response({"message": "Permission records deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def available_leaves(self, request, pk=None):
        """
        Get the final available leaves for the logged-in employee.
        """
        try:
            # Assuming user is authenticated and linked to an employee record
            employee = Employee.objects.get(user_id=pk)
            approved_permissions = Permission.objects.filter(
                employee_id=employee.employee_id,
                status="approved"
            )
            
            total_used_hours = sum(
                (p.time_to.hour + p.time_to.minute / 60) - (p.time_from.hour + p.time_from.minute / 60)
                for p in approved_permissions
            )

            # Total monthly leave hours
            total_monthly_leave = 2.0

            # Calculate available leave balance
            available_leave = max(0.0, total_monthly_leave - total_used_hours)
            permissions = Permission.objects.filter(user_id=pk)
            for permission in permissions:
                permission.avail_permission = available_leave 
                permission.save()

            return Response(
                {
                    "employee_id": employee.employee_id,
                    "employee_name": f"{employee.employee_first_name} {employee.employee_last_name}",
                    "total_monthly_leave": total_monthly_leave,
                    "used_leave_hours": total_used_hours,
                    "available_leave_hours": available_leave,
                },
                status=status.HTTP_200_OK,
            )

        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee record not found for the logged-in user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )