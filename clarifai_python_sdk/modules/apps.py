
class Apps:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def list_all(self):
        user_id = self.params['user_id']
        request_type = 'get'
        endpoint = self.params['endpoints']['apps']['list'](user_id)

        response = self.params['http_client'].make_request(
            method=request_type,
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)