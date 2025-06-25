from django.urls import path
from .views import get_user_ticket, get_assigned_ticket, TicketRetrieveUpdateDestroyView,add_category, open_tickets,delete_closed_tickets, get_categories, add_ticket, get_resolved_ticket,get_parent_categories
urlpatterns = [
    path('tickets/user/', get_user_ticket, name='user_ticket-list'),
    path('tickets/assigned/', get_assigned_ticket, name='assigned_ticket'),
    path('tickets/open/', open_tickets, name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketRetrieveUpdateDestroyView.as_view(), name='ticket-detail'),
    path('tickets/add-category/', add_category, name='add-category'),
    path('parent_category/', get_parent_categories, name='get-category'),
    path('category/', get_categories, name='post-category'),
    path('tickets/delete-closed/', delete_closed_tickets, name='delete-closed-tickets'),
    path('tickets/add/', add_ticket, name='add-ticket'),
    path('tickets/resolved/',get_resolved_ticket, name ='resolved')

]
