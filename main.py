from clarifai_python_sdk.client import ClarifaiApp

def main():
    config = {
        'token': '0ecced63ee6e42f18501bfd06a994d95',
        'user_id': 'excaliburne',
        'app_id': 'clarifai-toolbox-five',
        'response_config': {
            'pretty_print': True,
        }
    }    

    IMAGE_URL = 'https://assets.hansgrohe.com/celum/web/home_dream-bathroom_black-finish_16x9.jpg?format=HBW48'
    MODEL_ID = 'aaa03c23b3724a16a56b629203edc62c'

    clarifai = ClarifaiApp(**config)

    response = clarifai.apps.list_all()

    print(response)


if __name__ == "__main__":
    main()