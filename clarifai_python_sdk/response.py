# SYSTEM 
import json
from collections import namedtuple

# PACKAGE
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest


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
            _class = namedtuple('Test', field_names=['dict', 'json', 'status_code', 'description'])
            self.response = _class(
                dict=self._get_response_as_dict(response_dict),
                json=self._get_response_as_json(response_dict),
                status_code=self._get_satus_code_from_response(response_dict),
                description=self._get_status_description_from_response(response_dict)
            )

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
            additional_json_args = { 'indent': 2 }

        return json.dumps(response, **additional_json_args)