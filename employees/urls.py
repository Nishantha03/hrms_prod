from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from employees.views import UploadEmployeeExcelView, EmployeeViewSet, EventView, get_team_details, team_celebrations,team_member_counts,organizational_chart_view, get_employee_by_username, deactivate, get_employee_by_id
urlpatterns = [
    path('employees/', EmployeeViewSet.as_view(), name='employees'),
    path('employees/<int:pk>/', EmployeeViewSet.as_view(), name='employee-detail'),
    path('employee/event/', EventView.as_view(), name='process-employee-events'),
    path('employees/team/', get_team_details, name='get-team-details'), 
    path('employees/team/celebration/', team_celebrations, name='team_celebrations'),
    path('employees/team_count/', team_member_counts, name='team_count'),
    path('employees/chart/', organizational_chart_view, name='chart'),
    path('employees/<username>/', get_employee_by_username, name= 'username'),
    path('employees/deactivate/<int:pk>/', deactivate, name= 'deactivate'),
    path('profile/<int:pk>/', get_employee_by_id, name= 'id'),
    path('upload_employees/', UploadEmployeeExcelView.as_view(), name='upload-employees'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)