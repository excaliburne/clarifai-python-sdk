
class Concepts:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def get_all(self):
        request_type = 'get'
        endpoint = self.params['endpoints']['concepts']['list'](self.params['user_data_object'])

        response = self.params['http_client'].make_request(
            method=request_type,
            endpoint=endpoint
        )

        return self.params['response_object'].returns(response)