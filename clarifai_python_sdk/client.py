# MODULES
from clarifai_python_sdk.modules.apps import Apps
from clarifai_python_sdk.modules.models import Models
from clarifai_python_sdk.modules.response import Response
from clarifai_python_sdk.modules.inputs   import Inputs
from clarifai_python_sdk.modules.concepts import Concepts
from clarifai_python_sdk.modules.usage    import Usage

# HTTP CLIENT
from clarifai_python_sdk.http_client import HttpClient

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler

# CONSTANTS
from clarifai_python_sdk.constants import API_BASE_URL
from clarifai_python_sdk.endpoints import ENDPOINTS


class ClarifaiApi:
    def __init__(
        self,
        token: str,
        user_id: str = None,
        app_id: str = None,
        base_url: str = None,
        **kwargs
    ) -> None:
        
        self.token    = token
        self.user_id  = user_id or 'me'
        self.app_id   = app_id
        self.base_url = base_url or API_BASE_URL

        params = { 
            'token': self.token,
            'user_id': self.user_id,
            'app_id': self.app_id,
            'http_client': HttpClient(token=self.token, base_url=self.base_url),
            'endpoints': ENDPOINTS,
            'response_object': Response(params={**kwargs})
            # **kwargs
        }

        if self.user_id and self.app_id:
            params['user_data_object'] = {
                'user_id': self.user_id,
                'app_id': self.app_id
            }
        
        self.params = params
 
        self.apps     = Apps(params)
        self.models   = Models(params)
        self.inputs   = Inputs(params)
        self.concepts = Concepts(params)
        self.usage    = Usage(params)
    

    def me(self):
        """
        Who am I? 

        Returns:
            (Class): Wrapper
        """
        endpoint = UrlHandler().build('me')

        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)