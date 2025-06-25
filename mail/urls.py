from django.urls import path
from mail.views import send_message, inbox, sent_messages, delete_message, archive_message, mark_read_unread, archive

urlpatterns = [
    path("messages/send/", send_message, name="send_message"),
    path("messages/inbox/", inbox, name="inbox"),
    path("messages/sent/", sent_messages, name="sent_messages"),
    path('mail/delete/<int:pk>/', delete_message, name="delete-message"),
    path('mail/archive/<int:pk>/', archive_message, name="archive-message"),
    path('mail/read_action/<int:pk>/', mark_read_unread, name="mark-read-unread"),
    path('messages/archive/', archive, name="archive"),
]


    