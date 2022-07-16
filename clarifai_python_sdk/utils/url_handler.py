from clarifai_python_sdk.endpoints import ENDPOINTS

# UTILS
from clarifai_python_sdk.utils.dicts import delete_none_values, get_existing_dicts_from_keys


class UrlHandler:
    """
    All utils related to building and manipulating urls
    """

    @classmethod
    def build(
        cls, 
        endpoint_name: str,
        path_variables: dict = None,
        query_params: dict = None
        ) -> str:
        """
        Build a string for requested endpoint and feeds ids to pre-formatted string

        Args:
            endpoint_name (str)
            data (dict, optional): Url ids should be passed in a dict like {'user_id': 'xyz'}. Defaults to None.

        Returns:
            (String)
        """

        url               = ENDPOINTS[endpoint_name]
        query_params_list = []

        if (path_variables):
            url = getattr(url, 'format')(**delete_none_values(path_variables))
        
        if query_params:
            for idx, query_param in enumerate(query_params.items()):
                if query_param[1] is not None:
                    if idx == 0:
                        query = f'?{query_param[0]}={query_param[1]}'
                    else:
                        query = f'&{query_param[0]}={query_param[1]}'
                    
                    query_params_list.append(query)
                
        return url + ''.join(query_params_list)

    
    @classmethod
    def optional_pagination_url(
        cls, 
        page: str, 
        per_page: str
        ) -> dict:
        dict_to_return = {}

        if page and per_page:
            dict_to_return['page']     = page
            dict_to_return['per_page'] = per_page
        
        return dict_to_return
    

    @classmethod
    def optional_pagination_object(
        cls, 
        page: str, 
        per_page: str
        ) -> dict:
        dict_to_return = {'pagination': {}}

        if page and per_page:
            dict_to_return['pagination'] = {'page': page}
            dict_to_return['pagination'] = {'per_page': per_page}
        
        return dict_to_return