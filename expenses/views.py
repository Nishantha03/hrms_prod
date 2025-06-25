from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from expenses.models import Expenses
from .serializers import ExpenseSerializer, TravelExpenseSerializer, EmpExpenseSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions,status
from employees.models import Employee



@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def get_employee_expenses(request):
    """Retrieve all travel records for an employee."""
    user_data = request.user.id 
    userdata = request.data
    print(userdata)
    if userdata['category'] == "Travel":
        expenses = Expenses.objects.filter(category="Travel", employee_user_id = user_data)
        serializer = TravelExpenseSerializer(expenses, many=True)
    else:
        expenses = Expenses.objects.filter(employee_user_id = user_data,category=userdata['category'] )
        serializer = EmpExpenseSerializer(expenses, many=True)
    # expenses = Expenses.objects.filter(employee_user_id = user_data)
    # serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def sumbit_expenses(request):
    """Submit a new expense with username and department from Employee model."""
    try:
        employee = Employee.objects.get(user_id=request.user.id)  
        print(employee)
    except Employee.DoesNotExist:
        return Response({"error": "Employee record not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['emp_name'] = request.user.username  
    data['emp_department'] = employee.departmant  
    print(data)
    data = {key: value for key, value in data.items() if value not in ["", None, {}, []]}
    print(data)
    serializer = ExpenseSerializer(data=data)
    if serializer.is_valid():
        serializer.save() 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    print("Serializer validation errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])  
def expenses_update(request, pk):
    print(request.data)
    print("Incoming Files:", request.FILES)
    userdata = request.data.copy()
    userdata = request.data
    employee = Employee.objects.get(user_id=request.user.id)  
    userdata['emp_name'] = request.user.username  
    userdata['emp_department'] = employee.departmant 
    print(userdata)
    allowed_fields = {field.name for field in Expenses._meta.fields}  # Get model fields dynamically
    filtered_userdata = {key: value for key, value in userdata.items() if key in allowed_fields}
    print("Filtered Data:", filtered_userdata)
    if 'bills_upload' in request.FILES:
        filtered_userdata['bills_upload'] = request.FILES['bills_upload']
    else :
        filtered_userdata['bills_upload'] = None
    expense = Expenses.objects.get(id=pk)
    serializer = ExpenseSerializer(expense, data=userdata, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    print("Validation Errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  
def expenses_delete(request, pk):
    expense = Expenses.objects.get(id=pk)
    expense.delete()
    return Response({"message": "Message deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ExpenceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expenses.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  

        new_status = request.data.get('status')

        if not new_status:
            return Response({"error": "Status field is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = new_status
        instance.save()

        return Response(ExpenseSerializer(instance).data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_approved_rejected_expenses(request):
    """Retrieve expenses that are either approved or rejected."""
    expenses = Expenses.objects.filter(status__in=['Approved', 'Rejected'])
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_expenses(request):
    """Retrieve expenses that are still pending."""
    expenses = Expenses.objects.filter(status='Pending')
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expense_card(request):
    """Retrieve the count of total, approved, rejected, and pending expenses."""
    user = request.user.id

    total_requests = Expenses.objects.filter(employee_user_id=user).count()
    approved_count = Expenses.objects.filter(employee_user_id=user, status='Approved').count()
    rejected_count = Expenses.objects.filter(employee_user_id=user, status='Rejected').count()
    pending_count = Expenses.objects.filter(employee_user_id=user, status='Pending').count()

    return Response({
        "total_requests": total_requests,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "pending_count": pending_count,
    }, status=status.HTTP_200_OK)