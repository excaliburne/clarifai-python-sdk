# SYSTEM IMPORTS
from operator import itemgetter

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler


class Models:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    # TODO: 
    #   - 
    def predict(
        self, 
        inputs: list,
        model_id: str, 
        model_version_id: str = None
        ):
        """
        Predict endpoint

        Args:
            inputs (list)
            model_id (str)
            model_version_id (str, optional):  Defaults to None.

        Returns:
            (dict): Response dict
        """

        path_variables={
            'model_id'        : model_id,
            'model_version_id': model_version_id
        }

        endpoint = UrlHandler().build(
            'models__predict_without_version_id' if None in path_variables.values() else 'models__predict', 
            path_variables
        )

        inputs_payload = [{'data': input} for input in inputs]

        body = { 
            'user_app_id': self.params['user_data_object'],
            'inputs': inputs_payload
        }

        response = self.params['http_client'].make_request(
            method="post",
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns(response)


    def train(
        self,
        model_id: str
        ):
        """
        Start training a model 

        Args:
            model_id (str)

        Returns:
            (Response Object)
        """

        app_id   = itemgetter('app_id')(self.params)
        endpoint = UrlHandler().build('models__train', path_variables={'model_id': model_id, 'app_id': app_id})

        response = self.params['http_client'].make_request(
            method="post",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)

    
    def list(
        self,
        page: int = None,
        per_page: int = None
        ):
        """
        List models present in the app_id provided

        Args:
            page (int, optional): Defaults to None.
            per_page (int, optional): Defaults to None.

        Returns:
            (Response Object)
        """

        app_id   = itemgetter('app_id')(self.params)
        endpoint = UrlHandler().build(
            'models__list', 
            path_variables={'app_id': app_id},
            query_params={
                'page': page,
                'per_page': per_page
            }
        ) 

        response = self.params['http_client'].make_request(
            method="get",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)

    
    def list_model_types(
        self,
        page: int = None,
        per_page: int = None
        ):
        """
        List model types

        Args:
            page (int, optional): Defaults to None.
            per_page (int, optional): Defaults to None.

        Returns:
            (Response Object)
        """

        app_id   = itemgetter('app_id')(self.params)
        endpoint = UrlHandler().build(
            'models__list_model_types', 
            path_variables={'app_id': app_id},
            query_params={
                'page': page,
                'per_page': per_page
            }
        )

        response = self.params['http_client'].make_request(
            method="get",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)


    def get_model_by_id(self, model_id: str):
        """
        Get model by ID

        Args:
            model_id (str)

        Returns:
            (Response Object)
        """
        
        app_id   = itemgetter('app_id')(self.params)
        endpoint = UrlHandler().build(
            'models__get_model_by_id', 
            path_variables={'app_id': app_id, 'model_id': model_id}
        )

        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)


    def get_model_versions_by_model_id(
        self, 
        model_id: str,
        page: int = None,
        per_page: int = None
        ):
        """
        Get a list of model versions given a model_id

        Args:
            model_id (str)

        Returns:
            (Response Object)
        """

        app_id   = itemgetter('app_id')(self.params)
        endpoint = UrlHandler().build(
            'models__get_model_versions_by_model_id', 
            path_variables={ 'app_id': app_id, 'model_id': model_id} ,
            query_params={
                'page': page,
                'per_page': per_page
            }
        )

        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)

    
    def get_model_training_inputs(self, model_id: str):
        """
        Get a model's training inputs

        Args:
            model_id (str)

        Returns:
            (Response)
        """

        app_id   = itemgetter('app_id')(self.params)
        endpoint = UrlHandler().build(
            'models__get_model_training_inputs', 
            path_variables={ 'app_id': app_id, 'model_id': model_id } 
        )

        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)
