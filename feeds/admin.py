from django.contrib import admin
from .models import Announcement, Event, Post

admin.site.register(Announcement)
admin.site.register(Event)
admin.site.register(Post)
