from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.stats import mode

from algorithm.services.base import BaseAlgorithmService
from dataset.models import Dataset
from result.models import Result


class KNearestNeighborsService(BaseAlgorithmService):
    def knn_predict(
            self,
            p_values_train: NDArray[np.float64],
            p_values_test: NDArray[np.float64],
            s_values_train: NDArray[np.object],
            k: int
    ) -> Tuple[list[str], list[str]]:
        """
        Предсказание решения
        :param p_values_train: список обучающей выборки значений параметров
        :param p_values_test: список тестовой выборки значений параметров
        :param s_values_train: список обучающей выборка решений (id, value)
        :param k: число k
        :return: массив с предсказанными решениями, массив их айдишников
        """
        s_values_predict = []
        s_value_ids_predict = []
        for x_test in p_values_test:
            distances = np.linalg.norm(p_values_train - x_test, axis=1)
            nearest_neighbor_ids = distances.argsort()[:k]
            nearest_neighbor_value = s_values_train[nearest_neighbor_ids]
            prediction = mode(nearest_neighbor_value)
            s_values_predict.append(prediction.mode[0][1])
            s_value_ids_predict.append(prediction.mode[0][0])
        return s_values_predict, s_value_ids_predict

    def knn(self, dataset: Dataset, k: int, test_size: Optional[float] = 0.2, title: Optional[str] = None) -> Result:
        """
        Выполнение алгоритма
        :param dataset: Датасет
        :param k: число К
        :param test_size: процент тестовой выборки (0; 1.0)
        :param title: название для отчета
        :return: Модель результата
        """
        s_values_train, s_values_test = self.train_test_solution_values_split(dataset, test_size=test_size)
        p_values_train, p_values_test = self.extract_train_test_param_values(
            s_values_train=s_values_train,
            s_values_test=s_values_test
        )

        s_values_predict, s_value_ids_predict = self.knn_predict(
            p_values_train=p_values_train,
            s_values_train=np.array(s_values_train.values_list('id', 'value')),
            p_values_test=p_values_test,
            k=k
        )
        match_percentage = self.match_percantage(
            s_values_test=s_values_test.values_list('value', flat=True),
            s_values_predict=s_values_predict
        )

        result = self.create_report(
            dataset=dataset,
            match_percentage=match_percentage,
            s_values_train=s_values_train,
            s_values_test=s_values_test,
            s_value_ids_predict=s_value_ids_predict,
            title=title,
            k=k,
            test_size=test_size
        )

        return result
