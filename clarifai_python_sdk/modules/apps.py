from clarifai_python_sdk.utils.url_handler import UrlHandler

class Apps:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def list_all(self) -> dict:
        """
        List all apps given a user_id

        Returns:
            (dict): response object
        """
        user_id  = self.params['user_id']
        endpoint = UrlHandler().build('apps', {'user_id': user_id})

        response = self.params['http_client'].make_request(
            method="GET",
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)