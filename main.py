from clarifai_python_sdk.client import ClarifaiApi
from clarifai_python_sdk.modules.models import Models

def main():
    config = {
        'token': '',
        'user_id': '',
        'app_id': '',
        'response_config': {
            'pretty_print': True
            # 'convert_json_to_dict': True
        }
    }    

    IMAGE_URL = 'https://assets.hansgrohe.com/celum/web/home_dream-bathroom_black-finish_16x9.jpg?format=HBW48'
    MODEL_ID = 'e9576d86d2004ed1a38ba0cf39ecb4b1'

    clarifai = ClarifaiApi(**config)

    response = clarifai.models.predict(input_src=IMAGE_URL, model_id=MODEL_ID)

    print(response)


if __name__ == "__main__":
    main()