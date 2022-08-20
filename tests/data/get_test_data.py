from tests.data.python.inputs import IMAGES_UPLOAD_TEST_SET, VIDEOS_UPLOAD_TEST_SET
from tests.data.python.models import PREDICT_IMAGES_TEST_SET


class GetTestData:
    def __init__(self, name: str):
        self.name = name

    def __call__(self):
        return self._map_name_to_python_data(self.name)
    
    @staticmethod
    def _map_name_to_python_data(name: str): 
        dict_map = {
            'inputs__add__images': IMAGES_UPLOAD_TEST_SET,
            'inputs__add__videos': VIDEOS_UPLOAD_TEST_SET,
            'predict__images': PREDICT_IMAGES_TEST_SET
        }

        return dict_map.get(name)
