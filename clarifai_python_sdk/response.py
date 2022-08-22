# SYSTEM 
import json
from collections import namedtuple

# PACKAGE
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest
from clarifai_python_sdk.clarifai_status_codes import ClarifaiStatusCodes


class BuildResponseSchema:
    def __init__(
        self, 
        is_success: int = False,
        entries_if_success: dict = None,
        clarifai_status_code: int = None,
        clarifai_error_description: str = None
        ):

        self.is_success = is_success
        self.entries_if_success         = entries_if_success
        self.clarifai_status_code       = clarifai_status_code
        self.clarifai_error_description = clarifai_error_description

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def build(self) -> dict:
        response_schema = {
            'status': {
                'code': self.clarifai_status_code if self.clarifai_status_code else ClarifaiStatusCodes.SUCCESS,
                **({'description': self.clarifai_error_description} if self.clarifai_error_description else {})
            },
            **(self.entries_if_success if self.is_success else {})
        }

        return response_schema


class ResponseWrapper:
    def __init__(
        self, 
        params: dict,
        response_dict: dict = None,
        response_object: MakeClarifaiRequest = None
        ):

        self.params = params   

        if response_object:
            self.response = response_object

            setattr(self.response, 'dict', self._get_response_as_dict(self.response.response))
            setattr(self.response, 'json', self._get_response_as_json(self.response.response))
        
        elif response_dict:
            _class = namedtuple('Test', field_names=['dict', 'json', 'status_code', 'description', 'details'])
            self.response = _class(
                dict=self._get_response_as_dict(response_dict),
                json=self._get_response_as_json(response_dict),
                status_code=self._get_satus_code_from_response(response_dict),
                description=self._get_status_description_from_response(response_dict),
                details=self._get_status_details_from_response(response_dict)
            )
            
    @staticmethod
    def _get_status_details_from_response(response: dict) -> str or None:
        return response.get('status', {}).get('details')

    @staticmethod
    def _get_status_description_from_response(response: dict) -> str or None:
        return response.get('status', {}).get('description')

    @staticmethod
    def _get_satus_code_from_response(response: dict) -> int or None:
        return response.get('status', {}).get('code')

    @staticmethod
    def _get_response_as_dict(response: dict) -> str:
        return dict(response)
    
    def _get_response_as_json(self, response):
        additional_json_args = {}
        pretty_print         = self.params.get('response_config', {}).get('pretty_print_if_json') or True
        
        if pretty_print is not None and pretty_print == True:
            additional_json_args = {'indent': 2}

        return json.dumps(response, **additional_json_args)