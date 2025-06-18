from django.urls import path
from .views import HolidayView

urlpatterns = [
    path('holiday/', HolidayView.as_view(), name='holiday_list'),
]
