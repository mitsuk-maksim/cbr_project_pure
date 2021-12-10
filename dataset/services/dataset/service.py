from typing import Optional

from django.contrib.auth.models import User

from cbr_project_pure.functions import QueryType
from dataset.models import Dataset


class DatasetService:
    def __init__(self, *, user: Optional[User] = None):
        self.user = user

    def get_from_id(self, *, dataset_id: int) -> Optional[Dataset]:
        """
        Получение датасета по ID
        :param dataset_id:  ID датасета
        :return: датасет или ничего
        """
        return Dataset.objects.filter(id=dataset_id).first()

    def get_datasets(self) -> QueryType[Dataset]:
        datasets = Dataset.objects.filter(is_active=True)
        return datasets
