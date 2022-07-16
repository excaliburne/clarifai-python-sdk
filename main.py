from clarifai_python_sdk.client import ClarifaiApi


def main():
    config = {
        'token': '',
        'user_id': '',
        'app_id': '',
        'response_config': {
            'pretty_print_if_json': True
            # 'convert_json_to_dict': True
        }
    }    

    clarifai = ClarifaiApi(**config)

    # ...

if __name__ == '__main__':
    main()