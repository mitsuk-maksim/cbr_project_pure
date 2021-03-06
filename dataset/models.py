from enum import Enum
from typing import Dict, List, Optional

from django.conf import settings
from django.db import models
from django_enum_choices.fields import EnumChoiceField

from main.models import AbstractBaseModel


class ParameterTypes(str, Enum):
    integer = 'integer'
    float = 'float'
    string = 'string'


class Dataset(AbstractBaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='datasets',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=150, verbose_name='Название базы прецедентов')
    public = models.BooleanField(verbose_name='Публичность базы', default=True)

    def __str__(self):
        return self.title

    @staticmethod
    def create_dataset(
            title: str,
            param_info: List[Dict[str, str]],
            solution_info: Dict[str, str],
            user: Optional[settings.AUTH_USER_MODEL] = None,
    ) -> 'Dataset':
        """
        Создание пустой базы прецедентов
        :param title: название БП
        :param param_info: словарь из имени параметра и его типа
        :param solution_title: название результата
        :return: Dataset object
        """
        dataset = Dataset.objects.create(title=title, user=user)
        for param in param_info:
            type = param.get('type')
            Parameter.objects.create(
                title=param['title'],
                type=ParameterTypes[type] if type else None,
                description=param.get('description'),
                dataset=dataset
            )
        Solution.objects.create(
            title=solution_info['title'],
            dataset=dataset,
            description=solution_info.get('description')
        )
        return dataset


class Parameter(AbstractBaseModel):
    title = models.CharField(max_length=150, verbose_name='Название параметра')
    type = EnumChoiceField(ParameterTypes, default=ParameterTypes.float, null=True, blank=True)
    description = models.CharField(max_length=150, verbose_name='Описание параметра', null=True, blank=True)
    dataset = models.ForeignKey(Dataset, related_name='parameters', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Solution(AbstractBaseModel):
    title = models.CharField(max_length=150, verbose_name='Название решения')
    dataset = models.ForeignKey(Dataset, related_name='solutions', on_delete=models.CASCADE)
    description = models.CharField(max_length=150, verbose_name='Описание решения', null=True, blank=True)

    def __str__(self):
        return self.title


class SolutionValue(AbstractBaseModel):
    value = models.CharField(max_length=150, verbose_name='Значение результата')
    solution = models.ForeignKey(Solution, related_name='solution_values', on_delete=models.CASCADE)

    def __str__(self):
        return self.value


class ParameterValue(AbstractBaseModel):
    value = models.CharField(max_length=150, verbose_name='Значение параметра')
    parameter = models.ForeignKey(Parameter, related_name='parameter_values', on_delete=models.CASCADE)
    solution_value = models.ForeignKey(SolutionValue, related_name='parameter_values', on_delete=models.CASCADE)

    def __str__(self):
        return self.value
