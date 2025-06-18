
from django.db import models

class UserRequest(models.Model):
    user_id = models.IntegerField()
    user_email = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True,null=True)