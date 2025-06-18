
from rest_framework import status
from .models import Employee
from .serializers import EmployeeSerializer

def get_team(user):
    """
    Utility function to fetch employees with the same reporting manager as the user.
    """
    try:
        user_employee = Employee.objects.get(user=user)
        reporting_manager = user_employee.reporting_manager

        if not reporting_manager:
            # If there is no reporting manager, the user_employee is at the top of the hierarchy
            return {
                "error": False,  # Ensure "error" key is always present
                "message": "You are the top-level employee in the hierarchy.",
                "data": [EmployeeSerializer(user_employee).data],
            }, status.HTTP_200_OK

        # Get employees who report to the same manager
        employees = Employee.objects.filter(reporting_manager=reporting_manager)
        serializer = EmployeeSerializer(employees, many=True)
        return {
            "error": False,  # Ensure "error" key is always present
            "message": "Employees reporting to the same manager.",
            "data": serializer.data,
        }, status.HTTP_200_OK

    except Employee.DoesNotExist:
        return {
            "error": True,  # Ensure "error" key is always present
            "message": "Employee record not found.",
            "data": [],
        }, status.HTTP_404_NOT_FOUND
    except Exception as e:
        return {
            "error": True,  # Ensure "error" key is always present
            "message": str(e),
            "data": [],
        }, status.HTTP_500_INTERNAL_SERVER_ERROR
