import datetime

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q

from client.models import Doctor, Patient
from service.models import Services, Parameters

from utils.generatepdf import get_pdf


class PId(models.Model):
    p_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True)


class ParamResult(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True)
    param_id = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    res = models.TextField(null=True, blank=True)


class Result(models.Model):
    status_choices = (
        ('pending', 'pending'),
        ('progress', 'progress'),
        ('finished', 'finished')
    )

    id = models.BigAutoField(auto_created=True, primary_key=True, unique=True)
    service_id = models.ForeignKey(Services, on_delete=models.CASCADE)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    result = models.ManyToManyField(ParamResult)
    status = models.CharField(max_length=10, choices=status_choices, default='pending')


class Order(models.Model):
    status_choices = (
        ('pending', 'pending'),
        ('progress', 'progress'),
        ('finished', 'finished')
    )

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, unique=True)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='orderpatient')
    p_id = models.IntegerField(null=True, blank=True)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING, null=True, blank=True)
    services = models.ManyToManyField(Services, related_name='orderservice')
    results = models.ManyToManyField(Result, blank=True)
    status = models.CharField(max_length=30, choices=status_choices, default='pending')
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True)
    cost = models.IntegerField(null=True)
    file = models.URLField(null=True, blank=True)
    result_file = models.URLField(null=True, blank=True)
    p_file = models.URLField(null=True, blank=True)


@receiver(post_save, sender=ParamResult)
def change_result_status(sender, instance=None, created=False, **kwargs):
    if not created:
        res = ParamResult.objects.get(pk=instance.id).result_set.all()[0]
        if not Result.objects.get(pk=res.id).order_set.all()[0].results.filter(result__res__isnull=True).count():
            results = Result.objects.get(pk=res.id).order_set.all()[0].results.all()
            for i in results:
                Result.objects.filter(pk=i.id).update(status="finished")
            temp = Result.objects.get(pk=i.id)
            temp.status = "finished"
            temp.save()

        elif res.status == "pending":
            Result.objects.get(pk=res.id).order_set.update(status="progress")
            Patient.objects.filter(pk=res.patient_id.id).update(order_status="progress")
            res.status = "progress"
            res.save()


@receiver(post_save, sender=Result)
def change_order_status(sender, instance=None, created=False, **kwargs):
    if not created:
        order = Result.objects.get(pk=instance.id).order_set.all()[0]
        results = Order.objects.get(pk=order.id).results.filter(status__in=["pending", "progress"])
        if not results.count():
            order.status = "finished"
            order.save()


@receiver(post_save, sender=Order)
def change_status(sender, instance=None, created=False, **kwargs):
    if created:
        p_id = PId.objects.filter(pk=1)
        res_value = p_id[0].p_id
        patient = Patient.objects.filter(pk=instance.patient_id_id)
        patient.update(order_status="pending", timestamp=datetime.datetime.now(), p_id=res_value)
        res_value += 1
        p_id.update(p_id=res_value)

    elif not created:
        if instance.status == "finished":
            patient = Patient.objects.get(pk=instance.patient_id_id)
            patient.timestamp = datetime.datetime.now()
            patient.order_status = "finished"
            patient.doctor_id = None
            patient.save()
            if Order.objects.get(pk=instance.id).results.all().count() != 0:
                from .serializers import gen_order_file
                results = gen_order_file(instance.id)
                if len(results) != 0:
                    file_url = get_pdf(data=results, file_name=[str(instance.id), str(patient.id), patient.firstname])
                    Order.objects.filter(pk=instance.id).update(result_file=file_url)



