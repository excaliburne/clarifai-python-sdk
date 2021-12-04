# SYSTEM IMPORTS 
import json


class Response:
    def __init__(
        self,
        params: dict
        ):

        self.params = params

    
    def _response_object(
        self,
        object: dict, 
        pretty_print: bool = False,
        delete_status: bool = False,
        convert_json_to_dict: bool = False
        ):

        response = object

        if convert_json_to_dict:
            return dict(object)

        if delete_status:
            del response['status']

        if pretty_print:
            response = json.dumps(object, indent=4)

        return response


    def returns(self, response: dict):
        args = {}

        if self.params.get('response_config'):
            args = self.params['response_config']

        return self._response_object(object=response, **args)
