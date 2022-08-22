# SYSTEM 

# PACKAGE
from clarifai_python_sdk.response import ResponseWrapper
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest

# MODULES
from clarifai_python_sdk.modules.apps     import Apps
from clarifai_python_sdk.modules.models   import Models
from clarifai_python_sdk.modules.inputs   import Inputs
from clarifai_python_sdk.modules.concepts import Concepts
from clarifai_python_sdk.modules.usage    import Usage
from clarifai_python_sdk.modules.transfer import Transfer

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
        
        self._token    = token
        self._user_id  = user_id or 'me'
        self._app_id   = app_id
        self._base_url = base_url or API_BASE_URL

        params = { 
            'base_url': self._base_url,
            'token': self._token,
            'user_id': self._user_id,
            'app_id': self._app_id,
            'endpoints': ENDPOINTS,
            # **kwargs
        }

        params['user_app_id'] = {
            **({'user_id': self._user_id} if self._user_id else {}),
            **({'app_id': self._app_id} if self._app_id else {})
        }
        
        self.params = params
 
        self.apps     = Apps(params)
        self.models   = Models(params)
        self.inputs   = Inputs(params)
        self.concepts = Concepts(params)
        self.usage    = Usage(params)
        self.transfer = Transfer(
            params, 
            other_modules={'module_models': self.models, 'module_inputs': self.inputs, 'module_concepts': self.concepts}
        )
    
    def me(self, auth_object: dict = {}) -> ResponseWrapper:
        """
        Who am I? 

        Returns:
            (Object): ResponseWrapper
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="me",
            method="GET",
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)