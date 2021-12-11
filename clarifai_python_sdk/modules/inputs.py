# SYSTEM IMPORTS
import json
from operator import itemgetter

# ROOT
from clarifai_python_sdk import endpoints

# UTILS
from clarifai_python_sdk.utils.dicts import (
    get_dict_by_key_or_return_empty, get_existing_dicts_from_keys
)
from clarifai_python_sdk.utils.filters import Filters
from clarifai_python_sdk.utils.urls import Urls
from clarifai_python_sdk.utils.url_handler import UrlHandler


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


    def add(
        self, 
        inputs: list,
        convert_src: str = None
        ) -> dict:
        """Add inputs to Clarifai App

        Args:
            inputs (list): List of input objects

        Returns:
            (dict)
        """

        fail_to_upload_counter = 0  
        method = 'post'
        endpoint = UrlHandler().build('inputs__post')

        conversion_map = {
            'convert_url_to_base_64': lambda: [Urls().input_object_to_base64(input) for input in inputs]
        }

        if convert_src: inputs = conversion_map[convert_src]()

        body = { 
            'user_app_id': self.params['user_data_object'],
            'inputs': inputs
        }

        response = self.params['http_client'].make_request(
            method=method,
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns({
            'response': response,
            # 'fail_to_upload_counter': fail_to_upload_counter
        })
    
    
    def stream(
        self,
        per_page: int = 30,
        last_id: int = None
        ) -> dict:
        """Streaming (paginating) inputs in given Clarifai app

        Args:
            per_page (int, optional): Defaults to 30.
            last_id (int, optional): Defaults to None.

        Returns:
            (dict)
        """
        method = 'get'
        app_id = itemgetter('app_id')(self.params)
        endpoint = UrlHandler().build('inputs__stream', { 'app_id': app_id }) + f'?per_page={per_page}'
        inputs = []

        if last_id:
            endpoint = endpoint + f'&last_id={last_id}'

        response = self.params['http_client'].make_request(
            method=method,
            endpoint=endpoint
        )

        inputs = response['inputs']

        if response['status']['code'] == 10000 and len(inputs) > 0:
            last_id = inputs[-1]['id']

        return self.params['response_object'].returns({
            'inputs': inputs,
            'last_id': last_id
        })


    def list_all(self) -> dict:
        """Lists all inputs objects in app

        - Not recommended for large apps as output would be potentially too big

        Returns:
            (dict): { 'inputs', 'inputs_number' }
        """
        per_page = 10    
        last_batch_count_sould_be = per_page
        inputs = []
        last_batch = []

        def request_new_batch(**kwargs):
            nonlocal last_batch

            stream_inputs_response = self.stream(per_page=per_page, **kwargs)
            last_batch = stream_inputs_response['inputs']
            inputs.extend(last_batch)

        request_new_batch()

        while len(last_batch) == last_batch_count_sould_be:        
            last_id = last_batch[-1]['id']
            last_batch.clear()

            # Provide last_id to get the next set of inputs.
            request_new_batch(last_id=last_id)

        return self.params['response_object'].returns({
            'inputs': inputs,
            'inputs_number': len(inputs)
        })

    
    def delete_by_ids(
        self,
        inputs_ids: list
        ) -> dict:
        """Delete a list of inputs by input_ids

        Args:
            inputs_ids (list)

        Returns:
            (dict)
        """
        method = 'delete'
        endpoint = UrlHandler().build('inputs__post')
        
        body = { 
            'user_app_id': self.params['user_data_object'],
            'ids': inputs_ids
        }

        response = self.params['http_client'].make_request(
            method=method,
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns(response)


    def delete_all(self) -> dict:
        """Deletes all app inputs by streaming

        Returns:
            (dict): { 'number_of_deleted_inputs' }
        """
        per_page = 50
        last_batch_count_sould_be = per_page
        last_batch = []
        number_of_deleted_inputs = 0

        def request_new_batch(**kwargs):
            nonlocal number_of_deleted_inputs, last_batch

            stream_inputs_response = self.stream(per_page=per_page, **kwargs)
            last_batch = stream_inputs_response['inputs']
            self.delete_by_ids(Filters(last_batch).ids_from_input_objects())
            number_of_deleted_inputs = number_of_deleted_inputs + len(last_batch) 

        request_new_batch()

        while len(last_batch) == last_batch_count_sould_be:        
            last_id = last_batch[-1]['id']
            last_batch.clear()

            request_new_batch(last_id=last_id)
        
        return self.params['response_object'].returns({
            'number_of_deleted_inputs': number_of_deleted_inputs,
        })

