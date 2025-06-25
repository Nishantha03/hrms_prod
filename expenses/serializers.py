from rest_framework import serializers
from expenses.models import Expenses

class ExpenseSerializer(serializers.ModelSerializer):
    bills_upload = serializers.ImageField(required=False)
    class Meta:
        model = Expenses
        fields = "__all__"  
    def validate_bills_upload(self, value):
        if value in ["", None]:  
            return None 
        return value

class TravelExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields = ["id","employee_user_id", "emp_name", "from_date","to_date", "category",
                  "description", "amount", "payment_mode", "bills_upload",
                  "status", "travel_type"]  

class EmpExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields = ["id","employee_user_id", "emp_name", "from_date", "category",
                  "description", "amount", "payment_mode", "bills_upload",
                  "status"]  


        