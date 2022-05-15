from django.db import models

from service.models import Services


class Doctor(models.Model):
    id = models.CharField(max_length=6, primary_key=True, unique=True, serialize=True)
    firstname = models.CharField(max_length=100, null=True, blank=True)
    secondname = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=12, unique=True, null=True, blank=True)
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True, serialize=False)


class Patient(models.Model):
    gender_choice = (
        ('male', 'male'),
        ("female", "female")
    )
    status_choices = (
        ('pending', 'pending'),
        ('progress', 'progress'),
        ('finished', 'finished')
    )

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, unique=True)
    p_id = models.IntegerField(null=True, blank=True)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING, null=True, blank=True)
    firstname = models.CharField(max_length=100)
    secondname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    birth = models.IntegerField()
    gender = models.CharField(max_length=7, choices=gender_choice)
    phone = models.CharField(max_length=12, unique=True)
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True)
    order_status = models.CharField(max_length=24, choices=status_choices, default="pending")


