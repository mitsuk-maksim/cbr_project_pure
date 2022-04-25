from typing import Optional, Tuple

import numpy as np
from django.conf import settings
from django.db.models import QuerySet
from numpy.typing import NDArray

from dataset.models import SolutionValue, Dataset
from result.models import Result, SolutionPredictValueClass, ValueType, ParameterValueClass


class BaseAlgorithmService:
    def __init__(self, user: Optional[settings.AUTH_USER_MODEL] = None):
        self.user = user

    def extract_train_test_param_values(
            self, s_values_train: QuerySet[SolutionValue],
            s_values_test: QuerySet[SolutionValue]
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Достаем обучающую и тестовую выборку параметров из решений
        :param s_values_train: обучающие решения
        :param s_values_test: тестовые решения
        :return: списки значений параметров для обучающей и тестовой выборки
        """
        p_values_train, p_values_test = [], []
        for solution in s_values_train:
            p_values_train.append(list(solution.parameter_values.values_list('value', flat=True)))
        for solution in s_values_test:
            p_values_test.append(list(solution.parameter_values.values_list('value', flat=True)))
        p_values_train = np.array(p_values_train).astype('float64')
        p_values_test = np.array(p_values_test).astype('float64')
        return p_values_train, p_values_test

    def train_test_solution_values_split(
            self, dataset: Dataset, test_size: Optional[float] = 0.2
    ) -> Tuple[QuerySet[SolutionValue], QuerySet[SolutionValue]]:
        """
        Делим решения на обучающую и тестовую выборку значения решений
        :param dataset: Датасет
        :param test_size: процент тестовой выборки (0, 1.0)
        :return: обучающие и тестовые выборки
        """
        solutions = dataset.solutions.first().solution_values
        count = solutions.count()
        solution_ids = list(solutions.values_list('id', flat=True))
        test_size = round(count * test_size)
        np.random.shuffle(solution_ids)
        test_ids = solution_ids[:test_size]
        train_ids = solution_ids[test_size::]
        return solutions.filter(id__in=train_ids), solutions.filter(id__in=test_ids)

    def match_percantage(self, s_values_test: QuerySet[str], s_values_predict: list[str]) -> float:
        """
        Определение процента совпадение
        :param s_values_test: тестовая выборка решения
        :param s_values_predict: предсказанное решение
        :return: процент [0; 1.0]
        """
        if len(s_values_test) != len(s_values_predict):
            raise ValueError("s_values_test length is not equal with s_values_predict length")
        s_values_length = len(s_values_test)
        match_count = 0
        for i in range(s_values_length):
            if s_values_test[i] == s_values_predict[i]:
                match_count += 1
        percentage = match_count / s_values_length
        return round(percentage, 3)

    def create_report(
            self, dataset: Dataset,
            match_percentage: float,
            s_values_train: QuerySet[SolutionValue],
            s_values_test: QuerySet[SolutionValue],
            s_value_ids_predict: list[str],
            title: Optional[str] = None
    ) -> Result:
        """
        Создаем отчет по выполнению алгоритма
        :param dataset: Датасет
        :param s_values_train: решения обучающей выборки
        :param s_values_test: решений тестовой выборки
        :param s_value_ids_predict: id предсказанных решений
        :param match_percentage: процент совпадения
        :param title: название отчета
        :return: модель результата
        """
        result = Result.objects.create(
            title=title,
            match_percentage=match_percentage,
            dataset=dataset,
            user=self.user
        )

        SolutionPredictValueClass.objects.bulk_create([
            SolutionPredictValueClass(type=ValueType.test, result=result, solution_value_id=s_value_id)
            for s_value_id in s_value_ids_predict
        ])

        ParameterValueClass.objects.bulk_create([
            ParameterValueClass(type=ValueType.test, result=result, parameter_value=p_value)
            for s_value in s_values_test for p_value in s_value.parameter_values.all()
        ])

        ParameterValueClass.objects.bulk_create([
            ParameterValueClass(type=ValueType.train, result=result, parameter_value=p_value)
            for s_value in s_values_train for p_value in s_value.parameter_values.all()
        ])

        result.refresh_from_db()
        return result
