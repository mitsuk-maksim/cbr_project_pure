from enum import Enum

from django.db import models
from django_enum_choices.fields import EnumChoiceField

from main.models import AbstractBaseModel


class AlgorithmEnumType(str, Enum):
    KNN = 'kNN'


class Algorithm(AbstractBaseModel):
    title = models.CharField(max_length=128)
    type = EnumChoiceField(AlgorithmEnumType, null=True, default=None, unique=True)

    def __str__(self):
        return self.title
