class NotValidFileType(Exception):
    def __init__(self, *, file_name: str):
        self.err_message = f'File {file_name} with this type not valid'
        super().__init__(self.err_message)
