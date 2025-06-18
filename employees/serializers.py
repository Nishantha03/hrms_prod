from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class EmployeeSerializer(serializers.ModelSerializer):
    reporting_manager = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) 
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = "__all__"

    def get_reporting_manager(self, obj):
        """Return the reporting manager's name instead of the full object"""
        if obj.reporting_manager:
            return obj.reporting_manager.employee_first_name  # Assuming `employee_first_name` is the field
        return None

    def get_photo_url(self, obj):
        return obj.photo_url if obj.photo_url else None

    def create(self, validated_data):
        reporting_manager = validated_data.pop("reporting_manager", None)
        user = validated_data.pop("user", None)

        if reporting_manager:
            reporting_manager = Employee.objects.filter(employee_first_name=reporting_manager).first()
            if not reporting_manager:
                raise serializers.ValidationError({"reporting_manager": "Invalid reporting manager. No matching employee found."})

        employee = Employee.objects.create(
            **validated_data, reporting_manager=reporting_manager, user=user
        )
        return employee

    def update(self, instance, validated_data):
        if "reporting_manager" in validated_data:
            reporting_manager = validated_data.pop("reporting_manager", None)
            if reporting_manager:
                reporting_manager = Employee.objects.filter(employee_first_name=reporting_manager).first()
                if not reporting_manager:
                    raise serializers.ValidationError({"reporting_manager": "Invalid reporting manager. No matching employee found."})
                instance.reporting_manager = reporting_manager

        if "user" in validated_data:
            user = validated_data.pop("user")
            instance.user = user

        return super().update(instance, validated_data)
