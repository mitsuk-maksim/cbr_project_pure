from django.conf import settings
from django.db import models

from main.models import AbstractBaseModel
from result.models import Result


class DataSet(AbstractBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, related_name='datasets', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, verbose_name='Название базы прецедентов')
    public = models.BooleanField(verbose_name='Публичность базы', default=True)
    result = models.ForeignKey(Result, related_name='datasets', on_delete=models.CASCADE)


class Parameter(AbstractBaseModel):
    class Type(models.IntegerChoices):
        INT = 1, 'integer'
        FLOAT = 2, 'float'
        STR = 3, 'string'

    title = models.CharField(max_length=150, verbose_name='Название параметра')
    type = models.PositiveSmallIntegerField(choices=Type.choices)
    description = models.CharField(max_length=150, verbose_name='Описание параметра')
    data_set = models.ForeignKey(DataSet, related_name='parameters', on_delete=models.CASCADE)


class Solution(AbstractBaseModel):
    title = models.CharField(max_length=150, verbose_name='Название решения')
    data_set = models.ForeignKey(DataSet, related_name='solutions', on_delete=models.CASCADE)


class SolutionValue(AbstractBaseModel):
    value = models.CharField(max_length=150, verbose_name='Значение результата')
    solution = models.ForeignKey(Solution, related_name='solution_values', on_delete=models.CASCADE)


class ParameterValue(AbstractBaseModel):
    value = models.CharField(max_length=150, verbose_name='Значение параметра')
    parameter = models.ForeignKey(Parameter, related_name='parameter_values', on_delete=models.CASCADE)
    solution_value = models.ForeignKey(SolutionValue, related_name='parameter_values', on_delete=models.CASCADE)







