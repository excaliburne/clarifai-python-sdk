import json

from clarifai_python_sdk.client import ClarifaiApi
from clarifai_python_sdk.modules.models import Models

from clarifai_python_sdk.data import inputs
from clarifai_python_sdk.data import predict

def main():
    config = {
        'token': '0ecced63ee6e42f18501bfd06a994d95',
        'user_id': 'excaliburne',
        'app_id': 'clarifai-toolbox-five',
        'response_config': {
            'pretty_print': True,
            # 'convert_json_to_dict': True
        }
    }    

    clarifai = ClarifaiApi(**config)

    response = clarifai.concepts.list_all()

    print(response)


if __name__ == "__main__":
    main()