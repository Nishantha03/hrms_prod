from rest_framework import serializers
from .models import Leave_admin, Leave_admin_card




class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave_admin  
        fields = '__all__'

class AdminCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave_admin_card  
        fields = '__all__'   

