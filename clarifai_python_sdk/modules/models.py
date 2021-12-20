# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler

class Models:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def predict(
        self, 
        input_src: str,
        model_id: str, 
        model_version_id: str = None
        ):
        """
        Predict endpoint

        Args:
            input_src (str)
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
            'models__predict_without_version_id' if None is model_data.values else 'models__predict', 
            model_data
        )

        body = { 
            'user_app_id': self.params['user_data_object'],
            'inputs': [
                {
                    'data': {
                        'image': {
                            'url': input_src
                        }
                    }
                }
            ]
        }

        response = self.params['http_client'].make_request(
            method=request_type,
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns(response)