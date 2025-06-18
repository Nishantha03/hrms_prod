from django.urls import path, include
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, logout, register, is_logged_in, get_username, ForgotPasswordView,ResetPasswordView, change_password_view, get_pending_users, get_user_request,VerifyOTPView, get_all_users, GenerateOTPView


urlpatterns = [
    path('generate_otp/', GenerateOTPView.as_view(), name='generate_otp'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', logout),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register),
    path('authenticated/', is_logged_in),
    path('get_username/<int:pk>/', get_username, name='get_username'),
    path('forgot/', ForgotPasswordView.as_view(), name='forgot'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('reset/', ResetPasswordView.as_view(), name='reset-password'),
    path('change_password/', change_password_view, name='change_password'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('get_pending_user/', get_pending_users, name='get_pending_users'),
    path('get_user_request/', get_user_request, name='get_users'),
    path('get_all_user/', get_all_users, name='get_user_all'),

]
