# SYSTEM IMPORTS
from operator import itemgetter

# PACKAGE
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest
from clarifai_python_sdk.response              import ResponseWrapper
from clarifai_python_sdk.clarifai_status_codes import ClarifaiStatusCodes

# PACKAGES

# UTILS
from clarifai_python_sdk.utils.filters     import Filters
from clarifai_python_sdk.utils.data        import Data
from clarifai_python_sdk.utils.url_handler import UrlHandler
from clarifai_python_sdk.utils.decorators  import set_limits, handle_exception


class Search:
    def __init__(self, params: dict):
        self.params = params
    
    def _ranks_request(
        self,
        ranks: list,
        threshold: float or int,
        page: str,
        per_page: str,
        auth_object: dict = {}
        ) -> ResponseWrapper:

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

        response_object = MakeClarifaiRequest(
            endpoint_index_name="inputs__searches",
            method="POST",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id']),},
            body=body,
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)        

    def _filters_request(
        self,
        filters: list,
        page: int,
        per_page: int,
        auth_object: dict = {}
    ) -> ResponseWrapper:

        body = { 
            **UrlHandler.optional_pagination_object(page, per_page),
            'searches': [{
                'query': {
                    'filters': filters
                }
            }]
        }

        response_object = MakeClarifaiRequest(
            endpoint_index_name="inputs__searches",
            method="POST",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id']),},
            body=body,
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)        

    def filter_by_custom_concept(
        self,
        concepts: list,
        page: int = None, 
        per_page: int = None,
        auth_object: dict = {}
    ) -> ResponseWrapper:
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
            (Object) - ResponseWrapper
        """

        param_args = (page, per_page, auth_object)
        
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
        per_page: int = None,
        auth_object: dict = {}
    ) -> ResponseWrapper:
        """
        Rank by image based on visual similarity 

        Args:
            image_object (dict): Should look like...
                - { 'url': {URL_STRING} } ...with urls
                - { 'base64': {BASE64_STRING} } ...with base64
            page (int, optional)
            per_page (int, optional)

        Returns:
            (Object) - ResponseWrapper
        """
 
        param_args = (threshold, page, per_page, auth_object)

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
        per_page: int = None,
        auth_object: dict = {}
    ) -> ResponseWrapper:
        """
        Rank by input id based on visual similarity

        Args:
            input_id (str)
            threshold (float or int, optional)
            page (int, optional)
            per_page (int, optional)

        Returns:
            (Object) - ResponseWrapper
        """

        param_args = (threshold, page, per_page, auth_object)

        ranks = [{
            'annotation': {
                'input_id': input_id
            }
        }]

        return self._ranks_request(ranks, *param_args)


class Inputs:
    def __init__(self, params: dict):
        self.params = params
        self.search = Search(params)

    @handle_exception
    @set_limits({ 'inputs': (128, 1) })
    def add(
        self,
        inputs: list,
        auth_object: dict = {}
        ) -> ResponseWrapper:
        """Add inputs to Clarifai App

        Args:
            inputs (list): List of input objects
                            - See example of input objects in data/inputs/add_mock.py

        Returns:
            (Object) ResponseWrapper
        """

        for input in inputs:
            input_type = 'image' if input.get('image') else 'video'
            if input.get('convert_src_to_base64'):
                input[input_type]['base64'] = Data.image_url_to_base_64(input[input_type]['url'])
                del input[input_type]['url']
                del input['convert_src_to_base64']
        
        clarifai_api_final_formatting = list(map(lambda input: {'data': input}, inputs))

        body = { 
            'user_app_id': auth_object.get('user_app_id', self.params['user_app_id']),
            'inputs': clarifai_api_final_formatting
        }

        response_object = MakeClarifaiRequest(
            endpoint_index_name="inputs__post",
            method="POST",
            body=body,
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)
    
    def list(
        self,
        page: int = 1,
        per_page: int = 100,
        auth_object: dict = {}
    ):
        """
        List Inputs

        Args:
            page (int, optional): Defaults to 1.
            per_page (int, optional): Defaults to 100.
            auth_object (dict, optional):  Defaults to {}.

        Returns:
            _type_: _description_
        """
        response_object = MakeClarifaiRequest(
            endpoint_index_name="inputs__list",
            method="GET",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id'])},
            query_params={
                'page': page,
                'per_page': per_page
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)

    
    def stream(
        self,
        per_page: int = 128,
        last_id: int = None,
        auth_object: dict = {}
        ) -> ResponseWrapper:
        """Streaming (paginating) inputs in given Clarifai app

        Args:
            per_page (int, optional): Defaults to 128.
            last_id (int, optional): Defaults to None.

        Returns:
            (dict)
        """
        response_object = MakeClarifaiRequest(
            endpoint_index_name="inputs__stream",
            method="GET",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id'])},
            query_params={
                'per_page': per_page,
                'last_id': last_id
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)

    def list_all(self) -> dict:
        """Lists all inputs objects in app

        - Not recommended for large apps as output would be potentially too big

        Returns:
            (dict): { 'inputs', 'inputs_number' }
        """
        PER_PAGE                   = 100  
        LAST_BATCH_COUNT_SHOULD_BE = PER_PAGE

        inputs                    = []
        last_batch                = []
        is_listing_success        = True

        def request_new_batch(**kwargs):
            nonlocal last_batch

            stream_inputs_response = self.stream(per_page=PER_PAGE, **kwargs).response.dict
            last_batch             = stream_inputs_response.get('inputs', [])
            inputs.extend(last_batch)

        request_new_batch()

        while len(last_batch) == LAST_BATCH_COUNT_SHOULD_BE:        
            last_id = last_batch[-1]['id']
            last_batch.clear()

            # Provide last_id to get the next set of inputs.
            request_new_batch(last_id=last_id)

        response_schema = {
             'status': {
                'code': 10000 if is_listing_success else 10020
            },
            **({'inputs': inputs} if inputs else {})
        }

        return ResponseWrapper(self.params, response_dict=response_schema)

    @handle_exception
    @set_limits({ 'inputs_ids': (128, 1) })
    def delete_by_ids(
        self,
        inputs_ids: list,
        auth_object: dict = {}
        ) -> dict:
        """Delete a list of inputs by input_ids

        Args:
            inputs_ids (list)

        Returns:
            (dict)
        """

        body = { 
            'user_app_id': self.params['user_data_object'],
            'ids': inputs_ids
        }

        response_object = MakeClarifaiRequest(
            endpoint_index_name="inputs__post",
            method="DELETE",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id'])},
            body=body,
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)

    def delete_all(self) -> ResponseWrapper:
        """Deletes all app inputs by streaming

        Returns:
            (Object) - ResponseWrapper
        """
        per_page                  = 100
        last_batch_count_sould_be = per_page
        last_batch                = []
        number_of_deleted_inputs  = 0

        def request_new_batch(**kwargs):
            nonlocal number_of_deleted_inputs, last_batch

            stream_inputs_response = self.stream(per_page=per_page, **kwargs).response.dict
            last_batch             = stream_inputs_response['inputs']
            self.delete_by_ids(Filters(last_batch).ids_from_input_objects())
            number_of_deleted_inputs = number_of_deleted_inputs + len(last_batch) 

        request_new_batch()

        while len(last_batch) == last_batch_count_sould_be:        
            last_id = last_batch[-1]['id']
            last_batch.clear()

            request_new_batch(last_id=last_id)

        response_schema = {
            'status': {
                'code': ClarifaiStatusCodes.SUCCESS
            },
            'number_of_delete_inputs': number_of_deleted_inputs
        }
        
        return ResponseWrapper(
            self.params,
            response_dict=response_schema
        )

    def reupload_failed_inputs_as_base64(self):
        pass

    def reupload_existing_inputs_as_base64(self):
        pass
