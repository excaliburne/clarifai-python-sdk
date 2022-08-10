from clarifai_python_sdk.client import ClarifaiApi

config = {
    'token': '',
    'user_id': '',
    'app_id': '',
    'response_config': {
        'pretty_print_if_json': True,
    }
}    

clarifai = ClarifaiApi(**config)


# inputs.search
response = clarifai.inputs.search.rank_by_input_id(
    input_id="f21cd37f750a498d93e5926def533a19",
    threshold=0.8
).to_dict()

response = clarifai.inputs.search.filter_by_custom_concept(concepts=[{ 'name': 'sky' }]).to_dict()


# apps
response = clarifai.apps.create(id='test-app-4').to_json()
response = clarifai.apps.list().to_dict()
response = clarifai.apps.get('clarifai-toolbox-five').to_json()
response = clarifai.apps.delete(app_id="test-delete").to_json()
