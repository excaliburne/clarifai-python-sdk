# SYSTEM IMPORTS
import json

# UTILS
from clarifai_python_sdk.utils.dicts import (
    get_dict_by_key_or_return_empty, get_existing_dicts_from_keys
)


class Inputs:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def _get_input_struct_from_type(
        self, 
        input_src: str, 
        input_type: str
        ):

        struct = {}

        if input_type == 'url':
            struct['url'] = input_src
        
        return struct


    def add(self, inputs: list):
        """Add inputs to Clarifai App

        Args:
            inputs (list): List of input objects

        Returns:
            (dict)
        """

        fail_to_upload_counter = 0  
        list_of_responses = []
        method = 'post'
        endpoint = self.params['endpoints']['inputs']['post']

        for input in inputs:
            body = { 
                'user_app_id': self.params['user_data_object'],
                'inputs': [
                    {
                        'data': {
                            **get_existing_dicts_from_keys(input, ['image', 'video']), # should only find either in this case
                            **get_dict_by_key_or_return_empty(input, 'metadata'),
                            **get_dict_by_key_or_return_empty(input, 'concepts')
                        }
                    }
                ],
            }

            response = self.params['http_client'].make_request(
                method=method,
                endpoint=endpoint,
                body=body
            )
            list_of_responses.append(response)

        return self.params['response_object'].returns({
            'responses': list_of_responses,
            'fail_to_upload_counter': fail_to_upload_counter
        })