from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

from dataset.models import Dataset

"""
1. Нужно разбить параметры и решения на тестовые выборки (80% обучающие, 20% тестовые)
"""
class SckitService:

    def object_to_list(self, dataset_id: int):
        """
        Из датасета достаем Х - значения параметров, У - решение
        :param dataset_id:
        :type dataset_id:
        :return:
        :rtype:
        """

        # получаем словарь из айди-значения
        dataset = Dataset.objects.get(id=dataset_id)

        # не работает
        # X1 = np.array(pd.DataFrame(list(dataset.parameters.values(
        #     'id', 'parameter_values')
        # )).groupby('id').groups.values())
        #
        # Y1 = np.array(pd.DataFrame(list(dataset.solutions.values(
        #     'id', 'solution_values')
        # )).groupby('id').groups.values())

        X = []
        Y = []
        for parameter in dataset.parameters.all():
            X.append(list(parameter.parameter_values.values_list('value', flat=True)))
        for solution in dataset.solutions.all():
            Y.append(list(solution.solution_values.values_list('value', flat=True)))
        X = np.array(X).transpose().astype('float64')
        Y = np.array(Y)[0]
        print()
        return X, Y

    def knn(self, dataset_id: int):
        # url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
        # # Assign colum names to the dataset
        # names = ['sepal-length', 'sepal-width', 'petal-length', 'petal-width', 'Class']
        # # Read dataset to pandas dataframe
        # dataset = pd.read_csv(url, names=names)
        # X = dataset.iloc[:, :-1].values
        # y = dataset.iloc[:, 4].values

        X1, Y1 = self.object_to_list(dataset_id=dataset_id)
        # X_train, X_test, y_train, y_test = train_test_split(X1, Y1, test_size=0.20)
        X_train, X_test, y_train, y_test = self.train_test_split(X1, Y1, test_size=0.2)

        # масштабирование (не обязательно)
        # scaler = StandardScaler()
        # scaler.fit(X_train)
        #
        # X_train = scaler.transform(X_train)
        # X_test = scaler.transform(X_test)

        # обучение
        classifier = KNeighborsClassifier(n_neighbors=5)
        classifier.fit(X_train, y_train)

        # прогнозы по нашим тестовым данным
        y_pred = classifier.predict(X_test)

        # Оценка алгоритма
        print(confusion_matrix(y_test, y_pred))
        print(classification_report(y_test, y_pred))
