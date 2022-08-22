# SYSTEM
from operator import itemgetter
from ..clarifai_status_codes import ClarifaiStatusCodes

# PACKAGE
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest
from clarifai_python_sdk.response import ResponseWrapper

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler


class Models:
    def __init__(self, params: dict):
        self.params = params
    
    def predict(
        self, 
        inputs: list,
        model_id: str, 
        model_version_id: str = None,
        auth_object: dict = {}
        ) -> ResponseWrapper:
        """
        Predict endpoint

        Args:
            inputs (list)
            model_id (str)
            model_version_id (str, optional):  Defaults to None.

        Returns:
            (dict): Response dict
        """

        path_variables = {
            'model_id'        : model_id,
            'model_version_id': model_version_id
        }
        
        inputs_payload = [{'data': input} for input in inputs]

        body = { 
            'user_app_id': auth_object.get('user_app_id', {}) or self.params['user_app_id'],
            'inputs': inputs_payload,
        }

        response_object = MakeClarifaiRequest(
            endpoint_index_name="models__predict_without_version_id" if None in path_variables.values() else 'models__predict',
            method="POST",
            path_variables=path_variables,
            body=body,
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)

    def train(
        self,
        model_id: str,
        auth_object: dict = {}
        ) -> ResponseWrapper:
        """
        Start training a model 

        Args:
            model_id (str)

        Returns:
            (Response Object)
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="models__train",
            method="POST",
            path_variables={
                'model_id': model_id, 
                **(auth_object.get('user_app_id', {}) or self.params['user_app_id'])
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)

    def list(
        self,
        page: int = None,
        per_page: int = None,
        auth_object: dict = {}
        ) -> ResponseWrapper:
        """
        List models present in the app_id provided

        Args:
            page (int, optional): Defaults to None.
            per_page (int, optional): Defaults to None.

        Returns:
            (Response Object)
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="models__list",
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
    
    def list_model_types(
        self,
        page: int = None,
        per_page: int = None,
        auth_object: dict = {}
        ) -> ResponseWrapper:
        """
        List model types

        Args:
            page (int, optional): Defaults to None.
            per_page (int, optional): Defaults to None.

        Returns:
            (Response Object)
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="models__list_model_types",
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

    def get_model_by_id(self, model_id: str, auth_object: dict = {}) -> ResponseWrapper:
        """
        Get model by ID

        Args:
            model_id (str)

        Returns:
            (Response Object)
        """
        
        response_object = MakeClarifaiRequest(
            endpoint_index_name="models__get_model_by_id",
            method="GET",
            path_variables={
                **(auth_object.get('user_app_id', {}) or self.params['user_app_id']),
                'model_id': model_id
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)

    def get_model_versions_by_model_id(
        self, 
        model_id: str,
        page: int = None,
        per_page: int = None,
        auth_object: dict = {}
        ) -> ResponseWrapper:
        """
        Get a list of model versions given a model_id

        Args:
            model_id (str)

        Returns:
            (Response Object)
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="models__get_model_versions_by_model_id",
            method="GET",
            path_variables={
                **(auth_object.get('user_app_id', {}) or self.params['user_app_id']),
                'model_id': model_id
            },
            query_params={
                'page': page,
                'per_page': per_page
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)
    
    def get_model_training_inputs(self, model_id: str, auth_object: dict = {}) -> ResponseWrapper:
        """
        Get a model's training inputs

        Args:
            model_id (str)

        Returns:
            (Response)
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="models__get_model_training_inputs",
            method="GET",
            path_variables={
                **(auth_object.get('user_app_id', {}) or self.params['user_app_id']),
                'model_id': model_id
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)   

    def get_model_trained_concepts(
        self, 
        model_id: str, 
        model_version_id: str = None, 
        auth_object: dict = {}
        ) -> ResponseWrapper:
        """
        Retrieve model's trained concepts

        Args:
            model_id (str)
            model_version_id (str, optional)
            auth_object (dict, optional): Defaults to {}.

        Returns:
            (Object) - Response Wrapper

            {
                "status": {
                    "code": ...,
                    "description": ...,
                    "req_id": "c3a432aabe3c5..."
                },
                'concepts': [
                    {
                        'id': 'ai_jH6mzv12',
                        'name': 'Adriatic',
                        'value': 1,
                        'created_at': '2016-03-17T11:43:01.223962Z',
                        'language': 'en',
                        'app_id': '...'
                        ...
                    },
                    ...
                ]
            }
        """

        concepts = []
        endpoint_index_name = 'models__output_info' + '' if not model_version_id else '__with_version_id'

        response_object = MakeClarifaiRequest(
            endpoint_index_name=endpoint_index_name,
            method="GET",
            path_variables={
                **(auth_object.get('user_app_id', {}) or self.params['user_app_id']),
                'model_id': model_id,
                **({'version_id': model_version_id} if model_version_id else {})
            },
            auth_object=auth_object,
            package_params=self.params
        )

        if response_object.status_code == ClarifaiStatusCodes.SUCCESS:
            concepts = response_object.response['model']['output_info']['data']['concepts']

        response_schema = {
            'status': {**response_object.response['status']},
            'concepts': concepts
        }

        return ResponseWrapper(self.params, response_dict=response_schema)   

