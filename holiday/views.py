from datetime import datetime
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Holiday
from .serializers import HolidaySerializer


class HolidayView(APIView):
    def get(self, request):
        today = datetime.today() 
        current_year = today.year
        month_map = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        holidays = Holiday.objects.all()
        filtered_holidays = []

        for holiday in holidays:
            holiday_date = datetime(current_year, month_map[holiday.month], holiday.date)
            
            if holiday_date >= today:  
                filtered_holidays.append({
                    "date": f"{holiday.date} {holiday.month}",
                    "day": holiday.day,
                    "description": holiday.description,
                })
        return JsonResponse(filtered_holidays,safe=False)

    def post(self, request):
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
