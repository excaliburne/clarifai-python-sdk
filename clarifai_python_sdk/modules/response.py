# SYSTEM IMPORTS 
import json


class Wrapper:
    def __init__(
        self, 
        response,
        params
        ):
        self.response = response 
        self.params   = params   

    
    def to_dict(self):
        return dict(self.response)

    
    def to_json(self):
        additional_json_args = {}
        pretty_print         = self.params['response_config'].get('pretty_print_if_json')
        
        if pretty_print is not None and pretty_print == True:
            additional_json_args = { 'indent': 4 }

        return json.dumps(self.response, **additional_json_args)

class Response:
    def __init__(
        self,
        params: dict
        ):

        self.params = params


    def returns(self, response: dict):

        return Wrapper(response, self.params)