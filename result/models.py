from django.conf import settings
from django.db import models

from main.models import AbstractBaseModel


class Result(AbstractBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, related_name='result', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, verbose_name='Название результата')
    match_percentage = models.IntegerField(verbose_name="Процент совпадения")
