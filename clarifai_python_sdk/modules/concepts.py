# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler

class Concepts:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def list_all(self):
        request_type = 'get'
        endpoint = UrlHandler().build('concepts__list', {
            'app_id': self.params['user_data_object']['app_id'],
            'page': 1,
            'per_page': 500
        })

        response = self.params['http_client'].make_request(
            method=request_type,
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)