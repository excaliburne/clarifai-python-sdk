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
        data = None
        ) -> str:
        """
        Build a string for requested endpoint and feeds ids to pre-formatted strin

        Args:
            endpoint_name (str)
            data (dict, optional): Url ids should be passed in a dict like {'user_id': 'xyz'}. Defaults to None.

        Returns:
            (String)
        """

        url = ENDPOINTS[endpoint_name]

        if (data):
            data       = delete_none_values(data)
            pagination = get_existing_dicts_from_keys(data, ['page', 'per_page'])
            url        = getattr(url, 'format')(**data)

            if pagination:
                page     = pagination['page']
                per_page = pagination['per_page']
                url     += f'?page={page}&per_page={per_page}'

        return url