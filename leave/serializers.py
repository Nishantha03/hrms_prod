from rest_framework import serializers
from .models import Leave ,LeaveBalance 

from rest_framework import serializers
from .models import Leave
from datetime import date

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'

class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = '__all__'
