# SYSTEM

# PACKAGE
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest
from clarifai_python_sdk.response import ResponseWrapper

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler
from clarifai_python_sdk.utils import dicts


class Search:
    def __init__(self, params: dict):
        self.params = params

    def __call__(
        self, 
        name: str,
        sort_by_modified_at: bool = True,
        sort_by_name: bool = None,
        page: str = None,
        per_page: str = None,
        auth_object: dict = {}
        ) -> str or dict:
        """
        Search Clarifai apps by name

        Args:
            name (str)
            sort_by_modified_at (str, optional)
            page (str, optional)code 
            per_page (str, optional)

        Returns:
            (json or dict)
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="apps",
            method="GET",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id'])},
            query_params={
                'name': f'*{name}*',
                'sort_by_modified_at': None if sort_by_name == True else 'true',
                'sort_by_name': None if sort_by_modified_at == True or sort_by_name == None else 'true',
                'page': page,
                'per_page': per_page
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)    

class Apps:
    def __init__(self, params: dict):
        self.params = params
        self.search = Search(params)

    def create(
        self,
        id: str,
        name: str = None,
        default_language: str = None,
        default_workflow_id: str = None,
        auth_object: dict = {}
    ) -> ResponseWrapper: 
        """
        Create Clarifai Application

        Args:
            id (str)
            name (str, optional)
            default_language (str, optional)
            default_workflow_id (str, optional)

        Returns:
            (Object) - ResponseWrapper
        """

        args = dict(filter(lambda arg: arg[0] != 'self' and arg[1] is not None, locals().items()))

        json_body = {
            'apps': [args]
        }

        response_object = MakeClarifaiRequest(
            endpoint_index_name="apps",
            method="POST",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id'])},
            body=json_body,
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)    

    def get(self, app_id: str, auth_object: dict = {}) -> ResponseWrapper:
        """
        Get app by app_id

        Args:
            app_id (str)

        Returns:
            (Object) - ResponseWrapper
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="apps_with_app_id",
            method="GET",
            path_variables={**(auth_object.get('user_app_id', {}) or self.params['user_app_id'])},
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
        List all apps given a user_id.
        - If pagination arguments are not provided, it will return all apps

        Args:
            page (int)
            per_page (int)

        Returns:
            (Object): ResponseWrapper
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="apps",
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
    
    def delete(self, app_id: str, auth_object: dict = {}) -> ResponseWrapper:
        """
        Delete Clarifai application by app_id

        Args:
            app_id (str)

        Returns:
            (Object) - ResponseWrapper
        """

        # even though the "app_id" is present on the self.params['user_app_id']...
        # ...we want to make sure the app_id is explicitely specified while calling this function
        response_object = MakeClarifaiRequest(
            endpoint_index_name="apps_with_app_id",
            method="DELETE",
            path_variables={
                'app_id': app_id,
                **(auth_object.get('user_app_id', {}) or self.params['user_app_id'])
            },
            auth_object=auth_object,
            package_params=self.params
        )

        return ResponseWrapper(self.params, response_object=response_object)