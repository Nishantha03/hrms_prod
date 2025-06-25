from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from mail.models import Message
from mail.serializers import MessageSerializer
from employees.models import Employee

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_message(request):
    """
    Allows a user to send a message to another user.
    """
    employee = Employee.objects.get(user = request.user)
    sender =  request.user.email
    receiver = request.data.get("receiver")
    content = request.data.get("content")
    subject = request.data.get("subject", "")
    user_name = request.user.username
    user_image = employee.employee_photo.url  if employee.employee_photo else None
    attachment = request.FILES.get("attachment", None)

    if not receiver or not content:
        return Response({"error": "Receiver and content are required."}, status=status.HTTP_400_BAD_REQUEST)

    message = Message.objects.create(
        sender=sender, receiver=receiver, content=content, subject=subject, attachment=attachment, user_name = user_name, user_image = user_image
    )
    return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


# Get Messages for Logged-in User
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inbox(request):
    """
    Fetch all messages received by the logged-in user.
    """
    user_data = request.user
    receiver_mail = user_data.email
    messages = Message.objects.filter(receiver=receiver_mail, is_archived= False).order_by("-timestamp")
    # messages.user_name = 
    unread_count =  Message.objects.filter(receiver=receiver_mail, is_read= False, is_archived= False).count()
    serializer = MessageSerializer(messages, many=True)
    return Response({
        "unread_count": unread_count,
        "messages": serializer.data
    }, status=status.HTTP_200_OK)
# Get Sent Messages for Logged-in User
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sent_messages(request):
    """
    Fetch all messages sent by the logged-in user.
    """
    user_data = request.user
    sender_mail = user_data.email
    messages = Message.objects.filter(sender=sender_mail).order_by("-timestamp")
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_message(request, pk):
    """
    Delete a message by ID (Only the sender or receiver can delete).
    """
    try:
        message = Message.objects.get(id=pk)
        if message.sender != request.user.email and message.receiver != request.user.email:
            return Response({"error": "You are not authorized to delete this message."}, status=status.HTTP_403_FORBIDDEN)

        message.delete()
        return Response({"message": "Message deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Message.DoesNotExist:
        return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)

# Archive Message
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def archive_message(request, pk):
    """
    Archive a message.
    """
    try:
        message = Message.objects.get(id=pk)
        message.is_archived = True
        message.save()
        return Response({"message": "Message archived successfully."}, status=status.HTTP_200_OK)
    except Message.DoesNotExist:
        return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def archive(request):
    """
    Fetch all messages sent by the logged-in user.
    """
    user_data = request.user
    receiver_mail = user_data.email
    messages = Message.objects.filter(receiver=receiver_mail, is_archived=True).order_by("-timestamp")
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Mark as Read/Unread
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_read_unread(request, pk):
    """
    Toggle read/unread status of a message.
    """
    try:
        message = Message.objects.get(id=pk)
        message.is_read = True
        message.save()
        status_msg = "read" if message.is_read else "unread"
        return Response({"message": f"Message marked as {status_msg}."}, status=status.HTTP_200_OK)
    except Message.DoesNotExist:
        return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)