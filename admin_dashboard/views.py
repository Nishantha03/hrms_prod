from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Leave_admin, Leave_admin_card
from .serializers import AdminSerializer, AdminCardSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from .signals import send_approval_email_to_user


class AdminViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Leave_admin.objects.all().order_by('-id')
        serializer = AdminSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        """
        Handle PUT request to update a Leave_admin object by ID.
        """
        try:
            print(request.data)
            admin_leave = Leave_admin.objects.get(leave_id=pk)
        except Leave_admin.DoesNotExist:
            return Response({"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminSerializer(admin_leave, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminCardViewSet(APIView):
    def get(self, request):
        queryset = Leave_admin_card.objects.all()
        serializer = AdminCardSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk = None):
        """
        Handle DELETE request to delete a Leave_admin_card object by ID.
        """
        # delete_data = request.data 
        # leaveid = delete_data['leave_id']

        try:
            admin_card_leave = Leave_admin_card.objects.get(leave_id=pk)
            admin_card_leave.delete()
            return Response({"message": "Leave card record deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Leave_admin_card.DoesNotExist:
            return Response({"error": "Leave card record not found"}, status=status.HTTP_404_NOT_FOUND)
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def approve_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.is_active:
            return Response({"error": "User is already active."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        # Send email notification on admin approval
        send_approval_email_to_user(user.email, "Your account has been approved by the admin!")

        return JsonResponse({"message": "User approved and email sent."})
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
