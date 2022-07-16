# SYSTEM IMPORTS
# import json
from operator import itemgetter
from sqlite3 import paramstyle

# UTILS
from clarifai_python_sdk.utils.filters import Filters
from clarifai_python_sdk.utils.urls import Urls
from clarifai_python_sdk.utils.url_handler import UrlHandler


class Search:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def _ranks_request(
        self,
        ranks: list,
        threshold: float or int,
        page: str,
        per_page: str,
        ):

        endpoint = UrlHandler().build(
            'inputs__searches', 
            path_variables= {
                **self.params['user_data_object']
            }
        )

        additional_params = {}

        if threshold:
            additional_params['min_value'] = threshold

        body = { 
            **UrlHandler.optional_pagination_object(page, per_page),
            'searches': [{
                'query': {
                    'ranks': ranks
                },
                **additional_params
            }]
        }

        response = self.params['http_client'].make_request(
            method="POST",
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns(response)
    

    def _filters_request(
        self,
        filters: list,
        page: int,
        per_page: int 
    ):

        endpoint = UrlHandler().build(
            'inputs__searches', 
            path_variables={
                **self.params['user_data_object']
            }
        )

        body = { 
            **UrlHandler.optional_pagination_object(page, per_page),
            'searches': [{
                'query': {
                    'filters': filters
                }
            }]
        }

        response = self.params['http_client'].make_request(
            method="POST",
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns(response)


    def filter_by_custom_concept(
        self,
        concepts: list,
        page: int = None, 
        per_page: int = None
    ) -> str or dict:
        """
        Search inputs annotated with given concept name and value

        Args:
            concepts (list): Should look like:
                - [{"name": "sky", "value": 1}, ...] for positive annotations
                - [{"name": "sky", "value": O}, ...] for negative annotations
                - [{"name": "sky"}, ...] or without value
            page (int, optional)
            per_page (int, optional)

        Returns:
            (json str)
        """

        param_args = (page, per_page)
        
        filters = [{
            'annotation': {
                'data': {
                    'concepts': concepts
                }
            }
        }]

        return self._filters_request(filters, *param_args)
    

    def rank_by_image(
        self,
        image_object: dict,
        threshold: float or int = None,
        page: int = None,
        per_page: int = None
    ) -> str or dict:
        """
        Rank by image based on visual similarity 

        Args:
            image_object (dict): Should look like...
                - { 'url': {URL_STRING} } ...with urls
                - { 'base64': {BASE64_STRING} } ...with base64
            page (int, optional)
            per_page (int, optional)

        Returns:
            (json str or dict)
        """
 
        param_args = (threshold, page, per_page)

        ranks = [{
            'annotation': {
                'data': {
                    'image': image_object
                },
            }
        }]

        return self._ranks_request(ranks, *param_args)
    

    def rank_by_input_id(
        self,
        input_id: str,
        threshold: float or int = None,
        page: int = None,
        per_page: int = None
    ) -> str or dict:
        """
        Rank by input id based on visual similarity

        Args:
            input_id (str)
            threshold (float or int, optional)
            page (int, optional)
            per_page (int, optional)

        Returns:
            (json str or dict)
        """

        param_args = (threshold, page, per_page)

        ranks = [{
            'annotation': {
                'input_id': input_id
            }
        }]

        return self._ranks_request(ranks, *param_args)



class Inputs:
    def __init__(
        self,
        params
        ):
        self.params = params
        self.search = Search(params)


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

        endpoint = UrlHandler().build('inputs__post')

        conversion_map = {
            'convert_url_to_base_64': lambda: [Urls().input_object_to_base64(input) for input in inputs]
        }

        if convert_src: inputs = conversion_map[convert_src]()

        formatted_input_objects = [{'data': input} for input in inputs]

        body = { 
            'user_app_id': self.params['user_data_object'],
            'inputs': formatted_input_objects
        }

        response = self.params['http_client'].make_request(
            method="POST",
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns({
            'response': response,
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

        inputs   = []
        endpoint = UrlHandler().build(
            'inputs__stream',
            path_variables={ **self.params['user_data_object'] },
            query_params={
                'per_page': per_page,
                'last_id': last_id
            }
        )

        response = self.params['http_client'].make_request(
            method="GET",
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
        per_page                  = 10    
        last_batch_count_sould_be = per_page
        inputs                    = []
        last_batch                = []

        def request_new_batch(**kwargs):
            nonlocal last_batch

            stream_inputs_response = self.stream(per_page=per_page, **kwargs).to_dict()
            last_batch             = stream_inputs_response['inputs']
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

        endpoint = UrlHandler().build('inputs__post')
        
        body = { 
            'user_app_id': self.params['user_data_object'],
            'ids': inputs_ids
        }

        response = self.params['http_client'].make_request(
            method="DELETE",
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns(response)


    def delete_all(self) -> dict:
        """Deletes all app inputs by streaming

        Returns:
            (dict): { 'number_of_deleted_inputs' }
        """
        per_page                  = 50
        last_batch_count_sould_be = per_page
        last_batch                = []
        number_of_deleted_inputs  = 0

        def request_new_batch(**kwargs):
            nonlocal number_of_deleted_inputs, last_batch

            stream_inputs_response = self.stream(per_page=per_page, **kwargs).to_dict()
            last_batch             = stream_inputs_response['inputs']
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

