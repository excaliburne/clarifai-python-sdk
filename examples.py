from clarifai_python_sdk.client import ClarifaiApi

# Intialize API client
config = {
    'token': '',
    'user_id': '',
    'app_id': '',
    'response_config': {
        'pretty_print_if_json': True,
    }
}    

clarifai = ClarifaiApi(**config)


# -- MODULES... -- #

# apps
response = clarifai.apps.create(id='test-app-4').response.dict
response = clarifai.apps.list().response.dict
response = clarifai.apps.get('clarifai-toolbox-five').response.json
response = clarifai.apps.delete(app_id="test-delete").response.dict

# concepts

# models

# inputs.search
response = clarifai.inputs.search.rank_by_input_id(
    input_id="f21cd37f750a498d93e5926def533a19",
    threshold=0.8
).response.json
response = clarifai.inputs.search.filter_by_custom_concept(concepts=[{ 'name': 'sky' }]).response.dict

# inputs

# transfer

# usage
