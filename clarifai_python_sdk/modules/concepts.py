# SYSTEM 
from clarifai_python_sdk.make_clarifai_request import MakeClarifaiRequest
from clarifai_python_sdk.response              import ResponseWrapper 
from clarifai_python_sdk.clarifai_status_codes import ClarifaiStatusCodes

# UTILS
from clarifai_python_sdk.utils.url_handler import UrlHandler


class Concepts:
    def __init__(self, params: dict):
        self.params = params
    
    def list(
        self,
        page: int = 1,
        per_page: int = 100,
        auth_object: int = {}
    ) -> ResponseWrapper:
        """
        List concepts in app

        Args:
            page (str, optional): Defaults to 1.
            per_page (str, optional): Defaults to 100.

        Returns:
            (Object) - ResponseWrapper
        """

        response_object = MakeClarifaiRequest(
            endpoint_index_name="concepts__list",
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

    def list_all(self) -> ResponseWrapper:
        """
        List all concepts in app

        Returns:
            (Object) - ResponseWrapper
        """
        BATCH_SIZE = 100

        current_page = 1
        concepts     = []
        last_batch   = []

        def get_new_batch(page, per_page):
            get_page = self.list(page=page, per_page=per_page).response.dict
            concepts = get_page['concepts']

            return concepts
        
        first_batch = get_new_batch(current_page, BATCH_SIZE)
        concepts.extend(first_batch)
        last_batch = first_batch

        while len(last_batch) == BATCH_SIZE:
            new_batch = get_new_batch(current_page, BATCH_SIZE)
            concepts.extend(new_batch)
            current_page +=1
            last_batch = new_batch

        response_schema = {
            'status': {
                'code': ClarifaiStatusCodes.SUCCESS,
                'description': 'Ok'
            },
            **({'concepts': concepts} if concepts else {})
        }

        return ResponseWrapper(self.params, response_dict=response_schema)
