from django.db import models
from django.contrib.auth import get_user_model
from django_extensions.db.fields import ShortUUIDField
# Create your models here.

User = get_user_model()

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    bio = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    date_of_birth = models.DateField()
    image = models.FileField(upload_to='static/uploads', blank=True, null=True)
    gender = models.CharField(max_length=6, choices=(("male", "male"), ("female", "female")))
    address = models.TextField()
    slug = ShortUUIDField()
    patients = models.ManyToManyField("PatientProfile", blank=True)

    def __str__(self):
        return self.name



class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    date_of_birth = models.DateField()
    image = models.FileField(upload_to='static/uploads', blank=True, null=True)
    gender = models.CharField(max_length=6, choices=(("male", "male"), ("female", "female")))
    address = models.TextField()
    slug = ShortUUIDField()
    doctors = models.ManyToManyField(DoctorProfile, blank=True)

    def __str__(self):
        return self.name


class ConnectionRequest(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
