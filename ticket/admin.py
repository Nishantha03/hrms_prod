from django.contrib import admin

from ticket.models import Category, Ticket


admin.site.register(Category)
admin.site.register(Ticket)