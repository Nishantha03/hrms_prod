from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


from PIL import Image, ImageDraw, ImageFont

def generate_avatar(first_name, last_name):
    text = (first_name[:1] + last_name[:1]).upper()
    size = 100  # Avatar size
    image = Image.new("RGB", (size, size), (255, 255, 255))  # White background
    draw = ImageDraw.Draw(image)

    # Load font (Ensure arial.ttf is available, or use a default font)
    font = ImageFont.load_default()

    # Get text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Calculate text position (centered)
    x = (size - text_width) // 2
    y = (size - text_height) // 2

    # Draw text
    draw.text((x, y), text, font=font, fill=(0, 0, 0))

    # Convert to BytesIO
    image_io = BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)

    return ContentFile(image_io.getvalue(), f"{text}_avatar.png")


class Employee(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="employees", 
        null=True, 
        blank=True
    ) 
    employee_id = models.AutoField(primary_key=True) 
    employee_user_id = models.CharField(max_length=200)
    Salutation = models.CharField(max_length=50, blank=True, null=True)
    employee_first_name = models.CharField(
        max_length=200, null=False, 
    )
    employee_last_name = models.CharField(
        max_length=200, null=True, blank=True, 
    )
    email = models.EmailField(max_length=254, unique=True)
    contact_number = models.CharField(
        max_length=15,
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, 
    )
    qualification = models.CharField(max_length=50, blank=True, null=True)
    experience = models.IntegerField(null=True, blank=True)
    marital_status = models.CharField(
        max_length=50, blank=True, null=True
    )
    Workstream = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=20, null=True, blank=True)
    emergency_contact_relation = models.CharField(max_length=20, null=True, blank=True)
    departmant = models.CharField(max_length=100,null=True)
    reporting_manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subordinates'
    )
    designation = models.CharField(max_length=100, null=True)
    date_of_joining = models.DateField(null=True,blank=True)
    employee_photo = models.ImageField(
        upload_to='employee_photos/', 
        null=True, 
        blank=True
    )
    on_leave = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True) 
    biometric = models.IntegerField(null=True,blank=True)
    work_type = models.CharField(max_length=100, null=True, blank=True)  
    time_type = models.CharField(max_length=100, null=True, blank=True)  
    notice_period = models.CharField(max_length=100, null=True, blank=True) 
    experience_certificate = models.FileField(upload_to='certificates/experience/', null=True, blank=True)
    degree_certificate = models.FileField(upload_to='certificates/degree/', null=True, blank=True)
    marksheet = models.FileField(upload_to='certificates/marksheet/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate an avatar if no photo is provided.
        """
        if not self.employee_photo:
            avatar = generate_avatar(self.employee_first_name, self.employee_last_name)
            self.employee_photo.save(f"{self.employee_first_name}_avatar.png", avatar, save=False)
        
        super().save(*args, **kwargs)
        
        
    def get_full_name(self):
        """
        Method will return employee full name
        """
        return (
            f"{self.employee_first_name } {self.employee_last_name}"
            if self.employee_last_name
            else self.employee_first_name
        )
    @property
    def photo_url(self):
        """
        Returns the full URL of the employee photo.
        """
        if self.employee_photo:
            return self.employee_photo.url 
        return settings.MEDIA_URL + "default_avatar.png"
    
    def __str__(self):
        return self.employee_first_name
    
    
class Event(models.Model):
    EVENT_TYPES = (
        ('Birthday', 'Birthday'),
        ('Work Anniversary', 'Work Anniversary'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_date = models.DateField()
    employee_name = models.CharField(max_length=255) 
    employee_photo = models.ImageField(upload_to='event_photos/', null=True, blank=True)

