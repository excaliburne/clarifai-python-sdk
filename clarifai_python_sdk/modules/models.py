
class Models:
    def __init__(
        self,
        params
        ):
        self.params = params
    

    def predict(
        self, 
        input_src: str,
        model_id: str, 
        model_version_id: str = None
        ):
        """Predict

        Args:
            input_src (str): [description]
            model_id (str): [description]
            model_version_id (str, optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        model_data = {
            'model_id': model_id,
            'model_version_id': model_version_id
        }
        request_type = 'post'
        endpoint = self.params['endpoints']['models']['predict'](model_data)

        body = { 
            'user_app_id': self.params['user_data_object'],
            'inputs': [
                {
                    'data': {
                        'image': {
                            'url': input_src
                        }
                    }
                }
            ]
        }

        response = self.params['http_client'].make_request(
            method=request_type,
            endpoint=endpoint,
            body=body
        )

        return self.params['response_object'].returns(response)