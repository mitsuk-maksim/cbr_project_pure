class DatasetDoesNotExist(Exception):
    def __init__(self, *, dataset_id: str):
        self.err_message = f'Dataset with id {dataset_id} does not exist'
        super().__init__(self.err_message)
