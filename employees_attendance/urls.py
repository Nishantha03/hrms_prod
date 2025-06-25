from django.urls import path
from .views import get_regularize_data,pending_regularize,register_face, verify_face, get_data, get_weekly_attendance,SubmitRegularizationView, ApproveRegularizationView, RejectRegularizationView

urlpatterns = [
    path('register_face/', register_face, name='register_face'),
    path('verify_face/', verify_face, name='verify_face'),
    path('getdata/', get_data,name= 'data'),
    path('chart_data/', get_weekly_attendance, name='get_weekly_attendance'),
    path('pending_regularize/', pending_regularize, name='pending_regularize'),
    path('regularize/<int:pk>/', SubmitRegularizationView.as_view(), name='submit-regularization'),
    path('regularize/approve/<int:pk>/', ApproveRegularizationView.as_view(), name='approve-regularization'),
    path('regularize/reject/<int:pk>/', RejectRegularizationView.as_view(), name='reject-regularization'),
    path('get_regularize_data/',get_regularize_data, name='get_regularize_data'),
]

