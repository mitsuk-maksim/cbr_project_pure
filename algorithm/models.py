from django.db import models

from main.models import AbstractBaseModel
from result.models import Result


class Algorithm(AbstractBaseModel):
    title = models.CharField(max_length=128)
    result = models.ForeignKey(Result, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
