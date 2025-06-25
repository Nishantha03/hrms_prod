from django.db import models

class Holiday(models.Model):
    date = models.IntegerField()
    month = models.CharField(max_length=10)
    day = models.CharField(max_length=10)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.date} - {self.description}"
