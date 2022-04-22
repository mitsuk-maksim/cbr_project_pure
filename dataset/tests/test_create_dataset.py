import pytest

from dataset.models import Dataset, ParametersType


@pytest.mark.django_db
def test_create_dataset_with_one_param():
    param_info = [
        {'title': 'x1', 'type': ParameterTypes.float}
    ]
    dataset = Dataset.create_dataset(
        title='test_dataset',
        param_info=param_info,
        solution_title='y'
    )
    assert dataset.title == 'test_dataset'
    assert dataset.parameters.first().title == param_info[0]['title']
    assert dataset.parameters.first().type == param_info[0]['type']
    assert dataset.solutions.first().title == 'y'


@pytest.mark.django_db
def test_create_dataset_with_many_params():
    param_info = [
                     {'title': 'x1', 'type': ParameterTypes.integer},
                     {'title': 'x2', 'type': ParameterTypes.float},
                     {'title': 'x3', 'type': ParameterTypes.string},
                 ]
    dataset = Dataset.create_dataset(
        title='test_dataset',
        param_info=param_info,
        solution_title='y'
    )

    i = 0
    for param in dataset.parameters.all():
        assert param.title == param_info[i]['title']
        assert param.type == param_info[i]['type']
        i += 1

    assert dataset.solutions.first().title == 'y'
