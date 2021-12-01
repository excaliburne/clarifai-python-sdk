from clarifai_python_sdk.client import ClarifaiApi
from clarifai_python_sdk.modules.models import Models

def main():
    config = {
        'token': '0ecced63ee6e42f18501bfd06a994d95',
        'user_id': 'excaliburne',
        'app_id': 'clarifai-toolbox-five',
        'response_config': {
            'pretty_print': True
            # 'convert_json_to_dict': True
        }
    }    

    IMAGE_URL = 'https://assets.hansgrohe.com/celum/web/home_dream-bathroom_black-finish_16x9.jpg?format=HBW48'
    MODEL_ID = 'cccbe437d6e54e2bb911c6aa292fb072'

    clarifai = ClarifaiApi(**config)

    response = clarifai.models.predict(input_src=IMAGE_URL, model_id=MODEL_ID)

    print(response)


if __name__ == "__main__":
    main()