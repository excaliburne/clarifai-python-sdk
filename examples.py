from clarifai_python_sdk.client import ClarifaiApi

config = {
    'token': '',
    'user_id': '',
    'app_id': '',
    'response_config': {
        'pretty_print': True,
        # 'convert_json_to_dict': True
    }
}    

clarifai = ClarifaiApi(**config)


# inputs.search
response = clarifai.inputs.search.rank_by_input_id(
    input_id="f21cd37f750a498d93e5926def533a19",
    threshold=0.8
)

response = clarifai.inputs.search.filter_by_custom_concept(concepts=[{ 'name': 'sky' }])


# apps
response = clarifai.apps.create(id='test-app-4')
response = clarifai.apps.get('clarifai-toolbox-five')
response = clarifai.apps.delete(app_id="test-delete")
