import csv
from io import StringIO

import pytest

from dataset.models import Dataset
from dataset.services.dataset_upload import DatasetUploadService


@pytest.fixture()
def create_csv_file():
    mylist = [
        [1.1, 2.1, 3.1, 'first'],
        [1.2, 2.2, 3.2, 'second'],
        [1.3, 2.3, 3.3, 'third'],
    ]
    file = StringIO()
    csv.writer(file).writerows(mylist)
    file.seek(0)
    return file


@pytest.fixture()
def create_dataset():
    param_info = [
        {'title': 'x1'},
        {'title': 'x2'},
        {'title': 'x3'},
    ]
    dataset = Dataset.create_dataset(
        title='test_dataset',
        param_info=param_info,
        solution_title='y'
    )
    return dataset


@pytest.mark.django_db
def test_csv(create_dataset, create_csv_file):
    csv_file = create_csv_file
    dataset = create_dataset
    dataset_service = DatasetUploadService()
    dataset_service.upload_values_from_csv(dataset, file=csv_file)

