import time

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from service.models import Category


def file_dir_path(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = "user_photo/{}_{}.{}".format(str(time.time()), instance.user_id,  extension)
    return new_filename


class Photo(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='photo')
    photo = models.FileField(upload_to=file_dir_path, null=True, blank=True, verbose_name='image')

    def __str__(self):
        return f"{self.user_id}"

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"


class ChoiceCategories(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name='ID пользователя')
    categories = models.ManyToManyField(Category, verbose_name='Категории', related_name="choicecat")
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True, serialize=False)

    class Meta:
        verbose_name = "Категория Лаборанта"
        verbose_name_plural = "Категории Лаборантов"

    def __str__(self):
        return f"{self.user_id}"


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

