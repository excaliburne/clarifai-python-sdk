# SYSTEM
import copy

# PACKAGE
from clarifai_python_sdk.http_client import HttpClient

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler


class MakeClarifaiRequest:
    def __init__(
        self,
        endpoint_index_name: str,
        method: str,
        auth_object: dict,
        package_params: dict,
        path_variables: dict = None,
        query_params: dict = None,
        body: dict = None,
        ):
        
        self.endpoint_index_name = endpoint_index_name
        self.method         = method
        self.path_variables = path_variables
        self.query_params   = query_params
        self.auth_object    = auth_object
        self.package_params = package_params
        self.body           = body

        if not self.auth_object: # is None or empty dict
            self.auth_object = {
                'user_data_object': {
                    'user_id': self.package_params.get('user_id'),
                    'app_id' : self.package_params.get('app_id')
                },
                'token': self.package_params['token']
            }

        # can query
        self.status_code = None
        self.description = None
        self.details     = None
        self.response    = None
        self.data        = None

        self.make_request()

    def _filter_status_details_from_response(self) -> None:
        self.details = self.response.get('status', {}).get('details')

    def _filter_data_from_response(self) -> None:
        response_copy = copy.deepcopy(self.response)
        response_copy.pop('status')
        
        self.data = response_copy

    def _filter_status_code_from_response(self) -> None:
        self.status_code = self.response.get('status', {}).get('code')
    
    def _filter_status_description_from_response(self) -> None:
        self.description = self.response.get('status', {}).get('description')

    def make_request(self):
        endpoint = UrlHandler().build(
            self.endpoint_index_name,
            **({'path_variables': self.path_variables} if self.path_variables else {}),
            **({'query_params': self.query_params} if self.query_params else {})
        )

        response = HttpClient(
            token=self.auth_object['token'],
            base_url=self.package_params['base_url']
        ).make_request(
            method=self.method,
            endpoint=endpoint,
            **({'body': self.body} if self.body else {})
        )

        self.response = response
        self._filter_data_from_response()
        self._filter_status_code_from_response()
        self._filter_status_description_from_response()