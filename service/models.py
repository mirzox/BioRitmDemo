import time

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

# Create your models here.


class Category(models.Model):
    bool_choices = (
        (False, "Нет"),
        (True, "Да")
    )

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, unique=True)
    name = models.CharField(max_length=255, unique=True, verbose_name="Имя")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    items_count = models.IntegerField(default=0, verbose_name="Количество услуг")
    is_continuous = models.BooleanField(choices=bool_choices, default=False,
                                        verbose_name="Для этой категории CRM будет генерировать файлы?", null=True)
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True, serialize=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'


def file_dir_path(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = "template/{}_{}.{}".format(str(time.time()), instance.name,  extension)
    return new_filename


class Parameters(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, unique=True)
    name = models.CharField(max_length=255, unique=True, verbose_name="Название")
    norm = models.TextField(null=True, blank=True, verbose_name="Норма")
    file = models.FileField(upload_to=file_dir_path, null=True, blank=True, verbose_name="Файл")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'


class Services(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, unique=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='service',
                                    verbose_name="Категория")
    name = models.CharField(max_length=255, unique=True, verbose_name="Услуга")
    price = models.IntegerField(verbose_name="Цена")
    fee = models.IntegerField(verbose_name="Гонорар в %")
    parameters = models.ManyToManyField(Parameters, related_name='service_parameters', blank=True,
                                        verbose_name="Параметры")
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True, serialize=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Услугу'
        verbose_name_plural = 'Услуги'

    # def get_parameters(self):
    #     return "\n".join([p.name for p in self.parameters.all()])


@receiver(post_save, sender=Services)
def increment_items_count(sender, instance=None, created=False, **kwargs):
    if created:
        category = Category.objects.get(pk=instance.category_id.id)
        category.items_count = category.items_count+1
        category.save()


@receiver(post_delete, sender=Services)
def decrement_items_count(sender, instance=None, **kwargs):
    category = Category.objects.get(pk=instance.category_id.id)
    category.items_count = category.items_count - 1
    category.save()

