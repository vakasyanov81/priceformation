"""fake xls reader"""


class FakeXlsReader:
    """fake xls reader"""

    parse_result = None

    @classmethod
    def get_instance(cls, file_path, params):
        """get instance FakeXlsReader"""
        return FakeXlsReader(file_path, params)

    def __init__(self, file_path, params):
        """init"""
        self.file_path = file_path
        self.params = params
        self.sheet_indexes = None

    def parse(self, sheet_indexes: list = None):
        """do parse"""
        # pylint: disable=E1102

        self.sheet_indexes = sheet_indexes
        return self.parse_result() if callable(self.parse_result) else self.parse_result
