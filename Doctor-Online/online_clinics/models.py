from django.contrib.auth.hashers import make_password
from django.db import models

from .managers import DoctorManager, PatientManager


class BaseUser(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)


class Patient(BaseUser):
    objects = PatientManager()

    def __str__(self):
        return self.email

    def set_password(self):
        self.password = make_password(self.password)


class Doctor(BaseUser):
    objects = DoctorManager()

    def __str__(self):
        return self.email

    def set_password(self):
        self.password = make_password(self.password)


class Clinic(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='related_clinics', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f" Clinic Dr. {self.doctor.name} | {self.date} "


class Reservation(models.Model):
    clinic = models.ForeignKey(Clinic, related_name='reserved_patients', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, related_name='reserved_clinics', on_delete=models.CASCADE)
    time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.clinic.name} | {self.patient.name} | {self.time} "
