from django.urls import path
from .views import get_employee_expenses, sumbit_expenses, expenses_delete, expenses_update, ExpenceRetrieveUpdateDestroyView,get_approved_rejected_expenses, get_pending_expenses, get_expense_card

urlpatterns = [
    path('expenses/', get_employee_expenses, name='get_travel'),
    path('expenses/sumbit/', sumbit_expenses, name='create_travel'),
    path('expenses/update/<int:pk>/', expenses_update, name='update'),
    path('expenses/delete/<int:pk>/', expenses_delete, name='delete'),
    path('expenses/<int:pk>/', ExpenceRetrieveUpdateDestroyView.as_view(), name='Expenses-detail'),
    path('expenses/approved/', get_approved_rejected_expenses, name='get_approved_rejected'),
    path('expenses/pending/', get_pending_expenses, name='get_pending'),
    path('expenses_card/', get_expense_card, name='get_card'),
]