from typing import Optional

import numpy as np
from scipy.stats import mode
from dataset.models import Dataset
from result.models import Result


class KNearestNeighborsService:
    def object_to_list(self, dataset_id: int):
        """
        Из датасета достаем p_values - значения параметров, s_value - решение
        """
        dataset = Dataset.objects.get(id=dataset_id)
        p_values, s_value = [], []
        for parameter in dataset.parameters.all():
            p_values.append(list(parameter.parameter_values.values_list('value', flat=True)))
        for solution in dataset.solutions.all():
            s_value.append(list(solution.solution_values.values_list('value', flat=True)))
        p_values = np.array(p_values).transpose().astype('float64')
        s_value = np.array(s_value)[0]
        return p_values, s_value

    def train_test_split(self, p_values, s_value, test_size: Optional[float] = 0.2):
        """
        Разделяем на тестовую и обучающую выборки
        :param p_values: массив значений параметров
        :param s_value: массив решений
        :param test_size: размер тестовой выборки
        :return: p_values-обучающая, p_values-тестовая, s_value-обучающая, s_value-тестовая
        """
        if len(p_values) != len(s_value):
            raise ValueError("Parameter values length is not equal with solution value length")
        if 0 <= test_size >= 1:
            raise ValueError("test_size not in (0, 1.0) ")
        count = p_values.shape[0]
        test_size = round(count * test_size)
        # shufle lists
        indices = np.arange(count)
        np.random.shuffle(indices)
        p_values = p_values[indices]
        s_value = s_value[indices]

        return (
            p_values[test_size::],
            p_values[:test_size],
            s_value[test_size::],
            s_value[:test_size]
        )

    def match_percantage(self, s_value_test, s_value_predict):
        """
        Определение процента совпадение
        :param s_value_test: тестовая выборка решения
        :param s_value_predict: предсказанное решение
        :return: процент [0; 1.0]
        """
        if len(s_value_test) != len(s_value_predict):
            raise ValueError("s_value_train length is not equal with s_value_predict length")
        s_value_length = len(s_value_test)
        match_count = 0
        for i in range(s_value_length):
            if s_value_test[i] == s_value_predict[i]:
                match_count += 1
        percentage = match_count / s_value_length
        return round(percentage, 3)

    def knn_predict(self, p_values_train, p_values_test, s_value_train, k: int):
        """
        Предсказание решения
        :param p_values_train: обучающая выборка значений параметров
        :param p_values_test: тестовая выборка значений параметров
        :param s_value_train: обучающая выборка решений
        :param k:
        :return: массив с предсказанием решений
        """
        s_value_predict = []
        for x_test in p_values_test:
            distances = np.linalg.norm(p_values_train - x_test, axis=1)
            nearest_neighbor_ids = distances.argsort()[:k]
            nearest_neighbor_value = s_value_train[nearest_neighbor_ids]
            prediction = mode(nearest_neighbor_value)
            s_value_predict.append(prediction.mode[0])
        return s_value_predict

    def knn(self, dataset_id: int, k: int, title: Optional[str]):
        """
        Выполнение алгоритма
        :param dataset_id: Датасет
        :param k: число К
        :return: Модель результата с процентов совпадения
        """
        p_values, s_value = self.object_to_list(dataset_id=dataset_id)
        p_values_train, p_values_test, s_value_train, s_value_test = self.train_test_split(
            p_values, s_value, test_size=0.2
        )
        s_value_predict = self.knn_predict(
            p_values_train=p_values_train,
            s_value_train=s_value_train,
            p_values_test=p_values_test,
            k=k
        )
        match_percentage = self.match_percantage(s_value_test=s_value_test, s_value_predict=s_value_predict)
        result = Result.objects.create(
            title=title,
            match_percentage=match_percentage
        )
        return result