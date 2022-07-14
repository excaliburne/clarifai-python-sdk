# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler

class Concepts:

    def __init__(
        self,
        params
        ):
        
        self.params = params
    

    def list(
        self,
        page: str,
        per_page: str
    ):
        endpoint = UrlHandler().build('concepts__list', {
            'app_id': self.params['user_data_object']['app_id'],
            **UrlHandler.optional_pagination(page, per_page)
        })

        response = self.params['http_client'].make_request(
            method="get",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)


    def list_all(self):
        pass