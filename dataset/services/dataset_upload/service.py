from typing import Optional

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile

from dataset.models import Dataset, SolutionValue, ParameterValue


class DatasetUploadService:
    def upload_values(self, dataset: Dataset, *, file: InMemoryUploadedFile, csv_delimiter: Optional[str]):
        if 'csv' in file.name:
            self.upload_values_from_csv(dataset=dataset, file=file, csv_delimiter=csv_delimiter)

    def upload_values_from_csv(
            self,
            dataset: Dataset,
            *,
            file: InMemoryUploadedFile,
            csv_delimiter: Optional[str] = None
    ):
        column_name = (
            dataset.parameters.values_list('title', flat=True)[::1] +
            dataset.solutions.values_list('title', flat=True)[::1]
        )
        if not csv_delimiter:
            csv_delimiter = ','
        dataframe = pd.read_csv(file, header=None, names=column_name, sep=csv_delimiter)
        row_count = dataframe.shape[0]

        solution = dataset.solutions.first()

        for i in range(row_count):
            # create SolutionValue
            slt_value = dataframe.iloc[i][solution.title]
            solution_value = SolutionValue.objects.create(value=slt_value, solution=solution)

            # create ParameterValue
            for param in dataset.parameters.all():
                param_value = dataframe.iloc[i][param.title]
                ParameterValue.objects.create(
                    value=param_value,
                    parameter=param,
                    solution_value=solution_value
                )

        # file = file.read()
        # reader = csv.reader(io.StringIO(file))
        # for row in reader:
        #     print(row)
        #     if len(row) != dataset.parameters.count() + dataset.solutions.count():
        #         print('count exceptions')
        #
