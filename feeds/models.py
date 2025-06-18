from django.db import models
from django.contrib.auth.models import User

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='announcements/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    user_image = models.ImageField(upload_to='announcements/',null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True, default="")
    acknowledge_users = models.ManyToManyField(User, related_name='acknowledged_announcements', blank=True)
  

    def increment_acknowledge(self, user):
        if user not in self.acknowledge_users.all():
            self.acknowledge_users.add(user)
            self.save()

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    postid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_image = models.ImageField(upload_to='employee_photos/',null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True, default="")
    liked_users = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    acknowledge_users = models.ManyToManyField(User, related_name='acknowledged_posts', blank=True)
    department = models.CharField(max_length=255, null=True, blank=True, default="")
    is_approved = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
    )



    def increment_acknowledge(self, user):
        if user not in self.acknowledge_users.all():
            self.acknowledge_users.add(user)
            self.save()

    def __str__(self):
        return f"Post by {self.user.username}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user_image = models.ImageField(upload_to='employee_photos/',null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True, default="")

