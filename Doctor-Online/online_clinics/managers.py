from django.db import models


class PatientManager(models.Manager):

    def create_patient(self, **extra_fields):
        patient = self.model(**extra_fields)
        patient.set_password()
        patient.save(using=self._db)
        return patient


class DoctorManager(models.Manager):

    def create_doctor(self, **extra_fields):
        doctor = self.model(**extra_fields)
        doctor.set_password()
        doctor.save(using=self._db)
        return doctor
