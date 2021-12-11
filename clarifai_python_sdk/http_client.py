# SYSTEM IMPORTS
import requests, json

class HttpClient:
    def __init__(
        self,
        token: str,
        base_url: str
        ):
        self.token = token
        self.base_url = base_url


    def make_request(self, method, endpoint, body=None):
        args = {}
        req = getattr(requests, method)

        args['headers'] = {'Authorization': f'Key {self.token}'}
        
        if method == 'post':
            args['headers'] = {**args['headers'], 'Content-Type': 'application/json'}

        if body: 
            args['data'] = json.dumps(body)
        
        r = req(self.base_url + endpoint, **args)

        return r.json()