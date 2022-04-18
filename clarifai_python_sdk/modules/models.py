# SYSTEM IMPORTS
from operator import itemgetter

# UTILS
from urllib import response
from clarifai_python_sdk.utils.url_handler import UrlHandler


class Models:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def predict(
        self, 
        input_src: dict,
        model_id: str, 
        model_version_id: str = None
        ):
        """
        Predict endpoint

        Args:
            input_src (dict)
            model_id (str)
            model_version_id (str, optional):  Defaults to None.

        Returns:
            (dict): Response dict
        """

        model_data = {
            'model_id': model_id,
            'model_version_id': model_version_id
        }
        request_type = 'post'
            
        endpoint = UrlHandler().build(
            'models__predict_without_version_id' if None in model_data.values() else 'models__predict', 
            model_data
        )

        body = { 
            'user_app_id': self.params['user_data_object'],
            'inputs': [
                {
                    'data': input_src
                }
            ]
        }

        response = self.params['http_client'].make_request(
            method=request_type,
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns(response)


    def train(
        self,
        model_id: str
        ):

        app_id   = itemgetter('app_id')(self.params)
        endpoint = UrlHandler().build('models__train', data={'model_id': model_id, 'app_id': app_id})

        response = self.params['http_client'].make_request(
            method="post",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)