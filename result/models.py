from enum import Enum

from django.conf import settings
from django.db import models
from django_enum_choices.fields import EnumChoiceField

from dataset.models import Dataset, ParameterValue, SolutionValue
from main.models import AbstractBaseModel


class ValueType(str, Enum):
    train = 'train'
    test = 'test'


class Result(AbstractBaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='result',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=150, verbose_name='Название результата')
    match_percentage = models.FloatField(verbose_name="Процент совпадения")
    dataset = models.ForeignKey(Dataset, related_name='results', on_delete=models.CASCADE)
    parameter_values = models.ManyToManyField(ParameterValue, through='ParameterValueClass')
    solution_predict_values = models.ManyToManyField(SolutionValue, through='SolutionPredictValueClass')


class ParameterValueClass(AbstractBaseModel):
    type = EnumChoiceField(ValueType, null=True, default=None)
    parameter_value = models.ForeignKey(ParameterValue, on_delete=models.CASCADE)
    result = models.ForeignKey(Result, on_delete=models.CASCADE)


class SolutionPredictValueClass(AbstractBaseModel):
    type = EnumChoiceField(ValueType, null=True, default=None)
    solution_value = models.ForeignKey(SolutionValue, on_delete=models.CASCADE)
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
