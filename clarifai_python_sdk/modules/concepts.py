# SYSTEM IMPORTS
import json

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler


class Concepts:

    def __init__(
        self,
        params
        ):
        
        self.params = params
    

    def list(
        self,
        page: int = 1,
        per_page: int = 100
    ):
        """
        List concepts in app

        Args:
            page (str, optional): defaults to 1.
            per_page (str, optional): defaults to 100.

        Returns:
            (json or dict)
        """
        
        endpoint = UrlHandler().build(
            'concepts__list', 
            path_variables={
                'app_id': self.params['user_data_object']['app_id']
            },
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


    def list_all(self):
        """
        List all concepts in app

        Returns:
            (json or dict)
        """
        batch_size         = 100
        current_page       = 1
        concepts           = []
        last_batch         = []

        def get_new_batch(page, per_page):
            get_page = self.list(page=page, per_page=per_page).to_dict()
            concepts = get_page['concepts']

            return concepts
        
        first_batch = get_new_batch(current_page, batch_size)
        concepts.extend(first_batch)
        last_batch = first_batch

        while len(last_batch) == batch_size:
            new_batch = get_new_batch(current_page, batch_size)
            concepts.extend(new_batch)
            current_page +=1
            last_batch = new_batch

        return self.params['response_object'].returns({
            'status': {
                'code': 10000,
                'description': 'Ok'
            },
            'concepts': concepts
        })
