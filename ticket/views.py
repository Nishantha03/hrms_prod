from rest_framework import generics, permissions,status
from rest_framework.response import Response
from .models import Ticket,Category
from employees.models import Employee
from .serializers import TicketSerializer,CategorySerializer
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.utils.timezone import now



@api_view(['GET'])
def get_user_ticket(request):
    """Retrieve tickets created by the user"""
    user = request.user
    user_ticket = Ticket.objects.filter(created_by=user).order_by('-created_at')
    total_tickets = user_ticket.count()
    open_tickets = user_ticket.filter(status="open").count()
    closed_tickets = user_ticket.filter(status="closed").count()

    serialized_tickets = TicketSerializer(user_ticket, many=True).data

    response_data = {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "tickets": serialized_tickets
    }

    return Response(response_data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_assigned_ticket(request):
    """Retrieve tickets assigned to the user and handle escalation"""
    
    user = request.user
    assigned_tickets = Ticket.objects.filter(assigned_user=user)
    employee = Employee.objects.filter(user=user).first()  
    
    if employee and employee.reporting_manager:
        reporting_manager = employee.reporting_manager.user  
        
        for ticket in assigned_tickets:
            if ticket.status == "open" and ticket.escalation and now() > ticket.escalation:
                ticket.assigned_user = reporting_manager  
                ticket.escalation = None  
                ticket.save()
    
    # Re-fetch tickets after possible updates
    updated_tickets = Ticket.objects.filter(assigned_user=user)
    total_tickets = updated_tickets.count()
    open_tickets = updated_tickets.filter(status="open").count()
    closed_tickets = updated_tickets.filter(status="closed").count()
    serialized_tickets = TicketSerializer(updated_tickets, many=True).data

    response_data = {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "tickets": serialized_tickets
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_resolved_ticket(request):
    """Retrieve tickets resolved for the user"""
    user = request.user
    print(user)
    resolved_ticket = Ticket.objects.filter( created_by = user , status = "resolved")
    serialized_ticket = TicketSerializer(resolved_ticket, many=True).data
    print(serialized_ticket)
    return Response(serialized_ticket, status=status.HTTP_200_OK)


class TicketRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  

        new_status = request.data.get('status')

        if not new_status:
            return Response({"error": "Status field is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = new_status
        instance.save()

        return Response(TicketSerializer(instance).data, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_categories(request):
    """Retrieve categories and corresponding subcategories"""
    parent_name = request.data['parent']
    print(parent_name)
    if parent_name:
        parent_category = Category.objects.filter(name=parent_name).first()
        if not parent_category:
            return Response({"error": "Parent category not found."}, status=status.HTTP_404_NOT_FOUND)

        subcategories = Category.objects.filter(parent_name=parent_category)
        subcategories_list = [sub.name for sub in subcategories]
        print(subcategories_list)
        return Response(subcategories_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_parent_categories(request):
    """Retrieve categories and subcategories"""
    categories = Category.objects.all()
    # print(categories)
    response_data = []

    parent_categories = []

    for category in categories:
        if not category.parent_name:  
            parent_categories.append({"name": category.name})
        

    response_data = {
        "parents": parent_categories,
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_category(request):
    """Endpoint to add a new category or subcategory"""
    serializer = CategorySerializer(data=request.data)
    
    if serializer.is_valid():
        name = serializer.validated_data['name']
        parent_name = serializer.validated_data.get('parent_name', None)
        
        parent_category = Category.objects.filter(name=parent_name).first() if parent_name else None

        category = Category.objects.create(name=name, parent_name=parent_category.name if parent_category else None)
        
        return Response({"message": "Category added successfully!", "category": CategorySerializer(category).data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_ticket(request):
    """Create a new ticket and assign a user based on category and subcategory"""
    title = request.data.get('title')
    category_name = request.data.get('category')
    subcategory_name = request.data.get('subcategory')

    if not title or not category_name or not subcategory_name:
        return Response({"error": "Title, category, and subcategory are required"}, status=status.HTTP_400_BAD_REQUEST)

    category = Category.objects.filter(name=subcategory_name, parent_name=category_name).first()
    assigned_user = category.assigned_user if category else None  
    user_data = request.user
    created_user = user_data
    username = assigned_user.username if assigned_user else None
    
    ticket = Ticket.objects.create(
        title=title,
        category=category_name,
        subcategory=subcategory_name,
        priority = request.data.get('priority'),
        description = request.data.get('description'),
        assigned_user=assigned_user,
        created_by = created_user,
        username = username
    )
    files = request.FILES.getlist('files') 
    file_urls = []
    
    for file in files:
        file_path = f"ticket_attachments/{file.name}"
        with open(f"media/{file_path}", "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        file_urls.append(f"/media/{file_path}")

    ticket.attachment = file_urls
    
    ticket.save()
    return Response(
        {"message": "Ticket created successfully!", "ticket": TicketSerializer(ticket).data}, 
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
def open_tickets(request):
    """Endpoint to get all tickets with status 'Open'"""
    open_tickets = Ticket.objects.filter(status="open")  
    serializer = TicketSerializer(open_tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
def delete_closed_tickets(request):
    print("Received DELETE request to delete closed tickets :" , request)
    if request.method == 'DELETE':
        deleted_count, _ = Ticket.objects.filter(status="closed").delete()
        return JsonResponse({"message": f"Deleted {deleted_count} closed tickets."}, status=200)
    return JsonResponse({"error": "Invalid request method"}, status=400)
