from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

# Custom User model extending AbstractUser
class User(AbstractUser):
    # You can add additional fields here if needed
    pass

# Model for file uploads
class FileUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Ensure ForeignKey references your custom User model
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'File Uploads'  # Optional: Give a custom plural name for this model

    def __str__(self):
        return f"{self.file.name} uploaded by {self.user.username}"

# Model for patient details
class Patient(models.Model):
    unique_id = models.AutoField(primary_key=True)  # Automatically increments for each new patient
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    phone_number = models.CharField(max_length=15)
    admit_date = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    doctor_specialty = models.CharField(max_length=100)
    appointment_slot = models.CharField(max_length=100)
    problem = models.TextField()

    def __str__(self):
        return f'{self.first_name} {self.last_name} (ID: {self.unique_id})'
