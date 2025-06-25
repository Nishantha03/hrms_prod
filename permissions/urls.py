from django.urls import path, include
from rest_framework.routers import DefaultRouter
from permissions.views import PermissionRequestViewSet


permission_submit = PermissionRequestViewSet.as_view({'post': 'submit_form'})
permission_update = PermissionRequestViewSet.as_view({'put': 'update_status'})
permission_delete = PermissionRequestViewSet.as_view({'delete':'destroy'})
permission_list = PermissionRequestViewSet.as_view({'get':'list'})
permission_all = PermissionRequestViewSet.as_view({'get':'get_permission'})
availabe_permisssion = PermissionRequestViewSet.as_view({'get':'available_leaves'})

urlpatterns = [
   
    path('permission/submit/', permission_submit, name='submit_form'),
    path('permission/update/<int:pk>/', permission_update, name='update_status'),
    path('permission/delete/<int:pk>/', permission_delete, name='destroy'),
    path('permission/<int:pk>/', permission_list, name='list'),
    path('permission/', permission_all, name='get_permission'),
    path('permission/available/<int:pk>/', availabe_permisssion, name='available_leaves'),
    
] 


