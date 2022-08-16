# SYSTEM

# PACKAGE
from clarifai_python_sdk.clarifai_status_codes import ClarifaiStatusCodes

# MODULES
from clarifai_python_sdk.modules import Models, Concepts, Inputs


class Transfer:
    def __init__(
        self, 
        params: dict,
        other_modules: dict
        ):
        self.params = params

        self.origin_auth_object = {}
        self.to_auth_object     = {}

        # following modules should not be instanciated, they only serve as representation
        self.module_models   = Models   
        self.module_concepts = Concepts
        self.module_inputs   = Inputs

        for other_module in other_modules.items():
            setattr(self, other_module[0], other_module[1])

    def __call__(
        self,
        origin: dict,
        to: dict
        ):
        """

        Args:
            origin (dict): From which user/app
            to (dict): To which user/app

        Returns:
            self: _description_
        """

        self.origin_auth_object = {
            'user_app_id': {
                'user_id': origin['user_id'], 
                'app_id': origin['app_id']
            },
            'token': origin['token']
        }
        self.to_auth_object = {
            'user_app_id': {
                'user_id': to['user_id'], 
                'app_id': to['app_id']
            },
            'token': to['token']
        }

        return self

    def _list_inputs(
        self,
        page: int = 1,
        per_page = 128,
        auth_object: dict = {}
    ) -> list:
        kwargs = locals()
        kwargs.pop('self')

        response_list_inputs = self.module_inputs.list(**kwargs).to_dict()

        return response_list_inputs.get('inputs', [])
    
    def _upload_inputs(
        self,
        inputs: list,
        auth_object: dict = {}
    ) -> list:

        response_upload_inputs = self.module_inputs.add(inputs, auth_object).to_dict()

        return response_upload_inputs

    @staticmethod
    def _filter_input_objects(
        input_objects: dict,
        keep_annotations: bool = True,
        keep_metadata: bool = True
    ) -> list:
        """

        From:
            {
                "id": "f187936786fb4f628be1d6fb73422ae1",
                "data": {
                    "image": {
                        "url": "https://images.unsplash.com/photo-1605705658744-45f0fe8f9663?crop=entropy&cs=tinysrgb&fm=jpg&ixid=MnwzNDcxMTl8MHwxfHNlYXJjaHwyNnx8dHJ1Y2t8ZW58MHx8fHwxNjYwNTY1MTU5&ixlib=rb-1.2.1&q=80",
                        "hosted": {
                            "prefix": "https://s3.amazonaws.com/clarifai-api/img3/prod",
                            "suffix": "e303707711a3413f950d5d2e61bfccfc/05e402fdcbe082480f33b45fb6f208a1",
                            "sizes": [
                                "orig",
                                "tiny",
                                "small",
                                "large"
                            ]
                        },
                        "image_info": {
                            "width": 3329,
                            "height": 4993,
                            "format": "JPEG",
                            "color_mode": "YUV"
                        }
                    },
                    "concepts": [
                        {
                            "id": "horse",
                            "name": "horse",
                            "value": 1,
                            "app_id": "clarifai-toolbox-second"
                        }
                    ]
                },
                "created_at": "2022-08-15T12:07:02.944342Z",
                "modified_at": "2022-08-15T12:07:13.769193Z",
                "status": {
                    "code": 30000,
                    "description": "Download complete"
                }
            },
        To:
            {
                'image': {
                    'url': '...'
                },
                'metadata': {
                    'location': 'Paris'
                },
                'concepts': [
                    {'value': 1, 'id': 'iceland'}, 
                ]
            }

        Args:
            input_objects (dict): _description_
            keep_annotations (bool, optional): _description_. Defaults to True.
            keep_metadata (bool, optional): _description_. Defaults to True.
        """

        def filtered(input_object: dict) -> dict:
            image_or_video = input_object['data'].get('image') and 'image' or input_object['data'].get('video') and 'video'
            input_data     = input_object['data']
            input_src      = input_object['data'][image_or_video]
            has_concepts   = input_data.get('concepts')
            has_metadata   = input_data.get('metadata')
            has_hosted_url = input_src.get('hosted', {}).get('suffix')
            storage_url    = input_src['url']

            if has_hosted_url:
                storage_url = input_src['hosted']['prefix'] + '/large/' + input_src['hosted']['suffix']
            
            if has_concepts and keep_annotations:
                concepts = input_data.get('concepts')
                print(concepts)
                concepts = [{'value': concept['value'], 'id': concept['id']} for concept in concepts]

            return {
                image_or_video: {
                    'url': storage_url
                },
                **({'concepts': concepts} if has_concepts and keep_annotations else {}),
                **({'metadata': input_data.get('metadata')} if has_metadata and keep_metadata else {})
            }

        map_filtered = list(map(lambda input_object: filtered(input_object), input_objects))

        print(map_filtered)

        return map_filtered


    def inputs(
        self,
        inputs: list, # list of input_ids
        keep_annotations: bool = True,
        keep_metadata: bool = True
        ):
        pass

    def inputs_all(
        self,
        keep_annotations: bool = True,
        keep_metadata: bool = True
    ):
        PER_PAGE = 128

        responses_stack = []
        inputs       = []
        current_page = 1
        last_batch   = []

        def request_new_batch():
            list_orgin_inputs_response = self._list_inputs(
                page=current_page,
                per_page=PER_PAGE, 
                auth_object=self.origin_auth_object
            )
            
            return list_orgin_inputs_response or []
        
        last_batch = request_new_batch()
        current_page += 1
        response = self._upload_inputs(
            self._filter_input_objects(last_batch, keep_annotations, keep_metadata),
            auth_object=self.to_auth_object
        )
        responses_stack.append(response)

        while len(last_batch) == PER_PAGE:
            last_batch = request_new_batch()
            current_page += 1
            response = self._upload_inputs(
                self._filter_input_objects(last_batch, keep_annotations, keep_metadata),
                auth_object=self.to_auth_object
            )
            responses_stack.append(response)

        # response_schema = {
        #     'status': {
        #         'code': clarifai_status_code if clarifai_status_code is not None else ClarifaiStatusCodes.SUCCESS,
        #         **({'description': clarifai_error_description} if clarifai_error_description is not None else {})
        #     }
        # }

        return responses_stack

    def models(
        self,
        models: list
    ):
        """

        Args:
            models (list): Should look like...
                [
                    {
                        id: 'test',
                        version_id: '23455666dsdssds...'
                    }
                ] 
        """
        pass