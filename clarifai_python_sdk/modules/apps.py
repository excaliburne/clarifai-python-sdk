# SYSTEM IMPORTS

# 
from clarifai_python_sdk.utils.url_handler import UrlHandler

# UTILS
from clarifai_python_sdk.utils import dicts



class Search:
    def __init__(
        self,
        params
        ):
        self.params = params

    
    def __call__(
        self, 
        name: str,
        sort_by_modified_at: str = True,
        sort_by_name: str = None,
        page: str = None,
        per_page: str = None,
        ) -> str or dict:
        """
        Search Clarifai apps by name

        Args:
            name (str)
            sort_by_modified_at (str, optional)
            page (str, optional)
            per_page (str, optional)

        Returns:
            (json or dict)
        """

        endpoint = UrlHandler().build(
            'apps', 
            path_variables={**self.params['user_data_object']},
            query_params={
                'name': f'*{name}*',
                'sort_by_modified_at': None if sort_by_name == True else sort_by_modified_at,
                'sort_by_name': sort_by_name,
                'page': page,
                'per_page': per_page
            }
        )
        
        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint,
        )

        return self.params['response_object'].returns(response)


class Apps:
    def __init__(
        self,
        params
        ):
        self.params = params
        self.search = Search(params)

    
    def create(
        self,
        id: str,
        name: str = None,
        default_language: str = None,
        default_workflow_id: str = None
    ) -> str or dict: 
        """
        Create Clarifai Application

        Args:
            id (str)
            name (str, optional)
            default_language (str, optional)
            default_workflow_id (str, optional)

        Returns:
            (json or dict)
        """

        args = dict(filter(lambda arg: arg[0] != 'self' and arg[1] is not None, locals().items()))

        endpoint = UrlHandler().build('apps', path_variables={**self.params['user_data_object']})

        json_body = {
            'apps': [args]
        }

        response = self.params['http_client'].make_request(
            method="POST",
            endpoint=endpoint,
            body=json_body
        )

        return self.params['response_object'].returns(response)


    def get(self, app_id: str) -> str or dict:
        """
        Get app by app_id

        Args:
            app_id (str)

        Returns:
            (json or dict)
        """
        endpoint = UrlHandler().build(
            'apps_with_app_id', 
            path_variables={
                'user_id': self.params['user_data_object']['user_id'],
                'app_id': app_id
            }
        )

        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)


    def list_all(self) -> str or dict:
        """
        List all apps given a user_id

        Returns:
            (json or dict): response object
        """
        user_id  = self.params['user_id']
        endpoint = UrlHandler().build(
            'apps',
            path_variables={
                'user_id': user_id
            }
        )

        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)

    
    def delete(self, app_id: str) -> str or dict:
        """
        Delete Clarifai application by app_id

        Args:
            app_id (str)

        Returns:
            (json or dict)
        """

        # even though the "app_id" is present on the self.params['user_data_object']
        # we want to make sure the app_id is explicitely specified while calling this function
        endpoint = UrlHandler().build(
            'apps_with_app_id', 
            path_variables={
                'user_id': self.params['user_data_object']['user_id'],
                'app_id': app_id
            }
        )

        response = self.params['http_client'].make_request(
            method="DELETE",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)